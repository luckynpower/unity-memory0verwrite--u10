"""
Rooms screen — shows all 8 rooms with locked/playable/cleared states.
State key: "rooms"
"""
import pygame
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_YELLOW,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_TIER_COLOR = {1: ACCENT_GREEN, 2: ACCENT_CYAN, 3: ACCENT_ORANGE, 4: ACCENT_RED}
_TIER_LABEL = {1: "Tier 1  Entry Point", 2: "Tier 2  Technical",
               3: "Tier 3  Hacker Mindset", 4: "Tier 4  Deep Dive"}

# Card layout
_COLS    = 4
_ROWS    = 2
_CARD_W  = 270
_CARD_H  = 175
_GUTTER  = 18
_START_X = (SCREEN_WIDTH  - (_COLS * _CARD_W + (_COLS - 1) * _GUTTER)) // 2
_START_Y = 115
_HEADER_H = 80


class WorldMap(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_h1    = pygame.font.SysFont("consolas", 26, bold=True)
        self._font_room  = pygame.font.SysFont("consolas", 15, bold=True)
        self._font_body  = pygame.font.SysFont("consolas", 13)
        self._font_sm    = pygame.font.SysFont("consolas", 11)
        self._font_btn   = pygame.font.SysFont("consolas", 13)
        self._nodes: list[dict] = []
        self._tooltip_room: dict | None = None

    def on_enter(self, **kwargs) -> None:
        self._build_nodes()
        self._tooltip_room = None

    def _build_nodes(self) -> None:
        self._nodes = []
        for i, room in enumerate(ROOMS):
            col  = i % _COLS
            row  = i // _COLS
            x    = _START_X + col * (_CARD_W + _GUTTER)
            y    = _START_Y + row * (_CARD_H + _GUTTER)
            self._nodes.append({
                "room":    room,
                "rect":    pygame.Rect(x, y, _CARD_W, _CARD_H),
                "cleared": self.game.save.is_cleared(room["id"]),
                "score":   self.game.save.get_score(room["id"]),
            })

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.audio.play("click")
            self.game.sm.transition("main_menu")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for node in self._nodes:
                if node["room"]["available"] and node["rect"].collidepoint(event.pos):
                    self.game.audio.play("click")
                    self.game.sm.transition("room_game", room_id=node["room"]["id"])

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        mx, my = pygame.mouse.get_pos()
        self._tooltip_room = None
        for node in self._nodes:
            node["cleared"] = self.game.save.is_cleared(node["room"]["id"])
            node["score"]   = self.game.save.get_score(node["room"]["id"])
            if not node["room"]["available"] and node["rect"].collidepoint(mx, my):
                self._tooltip_room = node["room"]

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_header(surface)
        mx, my = pygame.mouse.get_pos()
        for node in self._nodes:
            self._draw_card(surface, node, (mx, my))
        self._draw_fragments_bar(surface)
        if self._tooltip_room:
            self._draw_tooltip(surface, self._tooltip_room, (mx, my))

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER, (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        title = self._font_h1.render("MEMORY0VERWRITE  //  ROOMS", True, ACCENT_CYAN)
        surface.blit(title, (28, 18))

        # Fragment counter
        cleared_count = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        frag = self._font_body.render(
            f"Memory fragments recovered:  {cleared_count} / {len(ROOMS)}",
            True, ACCENT_GREEN if cleared_count > 0 else TEXT_MUTED,
        )
        surface.blit(frag, (28, 50))

        hint = self._font_sm.render("ESC = Main Menu  |  M = toggle sound", True, TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 28, 32))

    def _draw_card(self, surface: pygame.Surface,
                   node: dict, mouse: tuple) -> None:
        room      = node["room"]
        rect      = node["rect"]
        available = room["available"]
        cleared   = node["cleared"]
        hovered   = rect.collidepoint(mouse) and available
        tier_col  = _TIER_COLOR.get(room["tier"], TEXT_DIM)

        # ── background ────────────────────────────────────────────────────────
        if cleared:
            fill = (10, 36, 20)
        elif hovered:
            fill = (18, 26, 48)
        elif available:
            fill = BG_PANEL
        else:
            fill = (10, 12, 20)
        pygame.draw.rect(surface, fill, rect, border_radius=7)

        # ── border ─────────────────────────────────────────────────────────────
        if cleared:
            border_col = ACCENT_GREEN
            bw = 2
        elif hovered:
            border_col = ACCENT_CYAN
            bw = 2
        elif available:
            border_col = BORDER
            bw = 1
        else:
            border_col = (20, 25, 40)
            bw = 1
        pygame.draw.rect(surface, border_col, rect, bw, border_radius=7)

        # ── tier stripe ───────────────────────────────────────────────────────
        stripe_col = tier_col if available else (25, 30, 50)
        pygame.draw.rect(surface, stripe_col,
                         pygame.Rect(rect.x + 2, rect.y + 2, rect.w - 4, 4),
                         border_radius=3)

        x0 = rect.x + 12
        y  = rect.y + 14

        # ── room number + title ───────────────────────────────────────────────
        num_col = ACCENT_GREEN if cleared else (ACCENT_CYAN if available else TEXT_MUTED)
        num  = self._font_room.render(f"Room {room['number']}", True, num_col)
        surface.blit(num, (x0, y))

        if cleared:
            score_s = self._font_sm.render(f"{node['score']} pts", True, ACCENT_GREEN)
            surface.blit(score_s, (rect.right - score_s.get_width() - 12, y + 2))

        y += num.get_height() + 3

        t_col  = TEXT_PRIMARY if available else TEXT_MUTED
        title  = self._font_room.render(room["title"], True, t_col)
        surface.blit(title, (x0, y))
        y += title.get_height() + 5

        # ── concept line ──────────────────────────────────────────────────────
        concept = self._font_sm.render(room.get("concept", ""), True,
                                       tier_col if available else TEXT_MUTED)
        surface.blit(concept, (x0, y))
        y += concept.get_height() + 6

        pygame.draw.line(surface, BORDER,
                         (x0, y), (rect.right - 12, y), 1)
        y += 8

        # ── teaser ────────────────────────────────────────────────────────────
        teaser_text = room.get("teaser", "")
        teaser_col  = TEXT_DIM if available else TEXT_MUTED
        teaser_lines = self._wrap(teaser_text, self._font_sm, rect.w - 24)
        for line in teaser_lines[:2]:
            ls = self._font_sm.render(line, True, teaser_col)
            surface.blit(ls, (x0, y))
            y += self._font_sm.get_height() + 2

        # ── status badge ──────────────────────────────────────────────────────
        if cleared:
            badge = self._font_btn.render("[  CLEARED  ]", True, ACCENT_GREEN)
        elif available:
            badge = self._font_btn.render(
                "[  ENTER  ]" if hovered else "[  AVAILABLE  ]",
                True, ACCENT_CYAN if hovered else ACCENT_GREEN,
            )
        else:
            badge = self._font_sm.render("[  LOCKED  ]", True, TEXT_MUTED)

        surface.blit(badge, (x0, rect.bottom - badge.get_height() - 10))

    def _draw_fragments_bar(self, surface: pygame.Surface) -> None:
        """Small dot row at bottom showing fragment collection progress."""
        total  = len(ROOMS)
        dot_r  = 5
        spacing = 18
        total_w = total * (dot_r * 2) + (total - 1) * (spacing - dot_r * 2)
        sx = SCREEN_WIDTH // 2 - total_w // 2
        y  = SCREEN_HEIGHT - 22

        for i, room in enumerate(ROOMS):
            x       = sx + i * spacing
            cleared = self.game.save.is_cleared(room["id"])
            col     = ACCENT_GREEN if cleared else (BORDER if room["available"] else TEXT_MUTED)
            pygame.draw.circle(surface, col, (x, y), dot_r, 0 if cleared else 1)

        label = self._font_sm.render("FRAGMENT PROGRESS", True, TEXT_MUTED)
        surface.blit(label, label.get_rect(centerx=SCREEN_WIDTH // 2, y=y + 10))

    def _draw_tooltip(self, surface: pygame.Surface,
                      room: dict, mouse: tuple) -> None:
        """Shows teaser + concept for locked rooms on hover."""
        lines = [
            room["title"],
            room.get("concept", ""),
            "",
            room.get("teaser", ""),
            "",
            "COMING SOON",
        ]
        font   = self._font_sm
        pad    = 12
        line_h = font.get_height() + 3
        max_w  = max(font.size(l)[0] for l in lines if l) + pad * 2
        box_h  = len(lines) * line_h + pad * 2

        mx, my = mouse
        tx = min(mx + 16, SCREEN_WIDTH  - max_w - 8)
        ty = min(my + 8,  SCREEN_HEIGHT - box_h  - 8)

        box = pygame.Rect(tx, ty, max_w, box_h)
        pygame.draw.rect(surface, BG_MID,  box, border_radius=5)
        pygame.draw.rect(surface, BORDER,  box, 1, border_radius=5)

        y = ty + pad
        for line in lines:
            if not line:
                y += line_h // 3
                continue
            if line == room["title"]:
                col = TEXT_PRIMARY
            elif line == "COMING SOON":
                col = TEXT_MUTED
            else:
                col = TEXT_DIM
            s = font.render(line, True, col)
            surface.blit(s, (tx + pad, y))
            y += line_h

    @staticmethod
    def _wrap(text: str, font: pygame.font.Font, max_w: int) -> list[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
