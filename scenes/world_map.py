"""
Rooms screen — shows all 8 rooms with locked/playable/cleared states.
State key: "rooms"
"""
import math
import random
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_GOLD,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_TIER_COLOR = {1: ACCENT_GREEN, 2: ACCENT_CYAN, 3: ACCENT_ORANGE, 4: ACCENT_RED}
_TIER_LABEL = {1: "Tier 1  Entry Point", 2: "Tier 2  Technical",
               3: "Tier 3  Hacker Mindset", 4: "Tier 4  Deep Dive"}

_COLS    = 4
_ROWS    = 2
_CARD_W  = 270
_CARD_H  = 175
_GUTTER  = 18
_START_X = (SCREEN_WIDTH  - (_COLS * _CARD_W + (_COLS - 1) * _GUTTER)) // 2
_START_Y = 115
_HEADER_H = 80

_GLITCH_CHARS  = "#@!%*?></"
_ARCHIVE_BTN   = pygame.Rect(SCREEN_WIDTH - 160, 50, 148, 22)
_ENDING_BTN    = pygame.Rect(SCREEN_WIDTH - 320, 50, 148, 22)


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
        self._time  = 0.0
        self._decays: dict[str, float] = {}
        # Pre-allocated surface for decay overlay (reused every frame)
        self._decay_surf = pygame.Surface((_CARD_W, _CARD_H), pygame.SRCALPHA)

    def on_enter(self, **kwargs) -> None:
        self._build_nodes()
        self._tooltip_room = None
        self._time  = 0.0
        self._decays = {}   # reset decay each time rooms screen is entered

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

    def _is_unlocked(self, room: dict) -> bool:
        """Sequential unlock: a room is unlocked if all prior available rooms are cleared."""
        available_rooms = [r for r in ROOMS if r["available"]]
        try:
            idx = available_rooms.index(room)
        except ValueError:
            return False
        if idx == 0:
            return True
        return self.game.save.is_cleared(available_rooms[idx - 1]["id"])

    def _can_enter(self, room: dict) -> bool:
        return room["available"] and self._is_unlocked(room)

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.audio.play("click")
            self.game.sm.transition("main_menu")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if _ARCHIVE_BTN.collidepoint(event.pos):
                self.game.audio.play("click")
                self.game.sm.transition("archive")
                return
            avail = [r for r in ROOMS if r["available"]]
            if avail and all(self.game.save.is_cleared(r["id"]) for r in avail):
                if _ENDING_BTN.collidepoint(event.pos):
                    self.game.audio.play("click")
                    self.game.sm.transition("ending", skip_to_stats=True)
                    return
            for node in self._nodes:
                if self._can_enter(node["room"]) and node["rect"].collidepoint(event.pos):
                    self.game.audio.play("click")
                    self.game.sm.transition("context", room_id=node["room"]["id"])

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        mx, my = pygame.mouse.get_pos()
        self._tooltip_room = None
        for node in self._nodes:
            room_id = node["room"]["id"]
            node["cleared"] = self.game.save.is_cleared(room_id)
            node["score"]   = self.game.save.get_score(room_id)
            if (not self._can_enter(node["room"]) and not node["cleared"]
                    and node["rect"].collidepoint(mx, my)):
                self._tooltip_room = node["room"]
            # Increment decay for cleared rooms — max 1.0 after ~70 seconds
            if node["cleared"]:
                self._decays[room_id] = min(
                    1.0,
                    self._decays.get(room_id, 0.0) + dt * 0.014,
                )

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_grid_bg(surface)
        self._draw_header(surface)
        mx, my = pygame.mouse.get_pos()
        for node in self._nodes:
            self._draw_card(surface, node, (mx, my))
        self._draw_fragments_bar(surface)
        fx.scanlines(surface, alpha=22)
        if self._tooltip_room:
            self._draw_tooltip(surface, self._tooltip_room, (mx, my))

    def _draw_grid_bg(self, surface: pygame.Surface) -> None:
        """Subtle dot-grid pattern for the cyber-world feel."""
        dot_spacing = 32
        dot_col     = (22, 30, 52)
        for x in range(0, SCREEN_WIDTH, dot_spacing):
            for y in range(_HEADER_H, SCREEN_HEIGHT - 30, dot_spacing):
                pygame.draw.circle(surface, dot_col, (x, y), 1)

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER, (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        title = self._font_h1.render("MEMORY0VERWRITE  //  ROOMS", True, ACCENT_CYAN)
        surface.blit(title, (28, 18))

        cleared_count  = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        avail_rooms    = [r for r in ROOMS if r["available"]]
        all_beaten     = bool(avail_rooms) and all(
            self.game.save.is_cleared(r["id"]) for r in avail_rooms
        )
        if all_beaten:
            frag = self._font_body.render(
                f"[ VIRUS DEFEATED ]  ·  ALL {len(avail_rooms)} FRAGMENTS RECOVERED",
                True, ACCENT_GREEN,
            )
        else:
            col  = ACCENT_GREEN if cleared_count > 0 else TEXT_MUTED
            frag = self._font_body.render(
                f"Memory fragments recovered:  {cleared_count} / {len(ROOMS)}", True, col
            )
        surface.blit(frag, (28, 50))

        hint = self._font_sm.render("ESC = Main Menu  |  M = toggle sound", True, TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 28, 22))

        mx, my    = pygame.mouse.get_pos()
        ab_hover  = _ARCHIVE_BTN.collidepoint((mx, my))
        ab_col    = ACCENT_CYAN if ab_hover else TEXT_DIM
        pygame.draw.rect(surface, BG_MID, _ARCHIVE_BTN, border_radius=3)
        pygame.draw.rect(surface, ab_col, _ARCHIVE_BTN, 1, border_radius=3)
        abt = self._font_sm.render("[ MEMORY ARCHIVE ]", True, ab_col)
        surface.blit(abt, abt.get_rect(center=_ARCHIVE_BTN.center))

        # VIEW ENDING button — only after all available rooms cleared
        if all_beaten:
            eb_hover = _ENDING_BTN.collidepoint((mx, my))
            eb_col   = ACCENT_GREEN if eb_hover else TEXT_DIM
            pygame.draw.rect(surface, BG_MID, _ENDING_BTN, border_radius=3)
            pygame.draw.rect(surface, eb_col,  _ENDING_BTN, 1, border_radius=3)
            ebt = self._font_sm.render("[ VIEW ENDING ]", True, eb_col)
            surface.blit(ebt, ebt.get_rect(center=_ENDING_BTN.center))

    def _draw_card(self, surface: pygame.Surface,
                   node: dict, mouse: tuple) -> None:
        room      = node["room"]
        rect      = node["rect"]
        cleared   = node["cleared"]
        can_enter = self._can_enter(room)
        locked    = room["available"] and not can_enter and not cleared
        hovered   = rect.collidepoint(mouse) and can_enter
        tier_col  = _TIER_COLOR.get(room["tier"], TEXT_DIM)
        idx       = ROOMS.index(room)

        # ── background ────────────────────────────────────────────────────────
        if cleared:
            fill = (20, 14, 4)
        elif hovered:
            fill = (18, 26, 48)
        elif can_enter:
            fill = BG_PANEL
        else:
            fill = (13, 8, 14)
        pygame.draw.rect(surface, fill, rect, border_radius=7)

        # ── border ─────────────────────────────────────────────────────────────
        if cleared:
            bw = 2; border_col = ACCENT_GOLD
        elif hovered:
            bw = 2; border_col = ACCENT_CYAN
        elif can_enter:
            bw = 1
            pulse = 0.40 + 0.30 * abs(math.sin(self._time * 1.6 + idx * 0.9))
            r0, g0, b0 = BORDER
            rc, gc, bc = ACCENT_CYAN
            border_col = (
                int(r0 + (rc - r0) * pulse),
                int(g0 + (gc - g0) * pulse),
                int(b0 + (bc - b0) * pulse),
            )
        elif locked:
            bw = 1; border_col = (50, 24, 38)
        else:
            bw = 1; border_col = (28, 14, 22)
        pygame.draw.rect(surface, border_col, rect, bw, border_radius=7)

        # ── tier stripe ───────────────────────────────────────────────────────
        if cleared or can_enter:
            stripe_col = tier_col
        elif locked:
            stripe_col = (30, 16, 24)
        else:
            stripe_col = (22, 12, 18)
        pygame.draw.rect(surface, stripe_col,
                         pygame.Rect(rect.x + 2, rect.y + 2, rect.w - 4, 4),
                         border_radius=3)

        x0 = rect.x + 12
        y  = rect.y + 14

        # ── room number ───────────────────────────────────────────────────────
        num_col = (ACCENT_GOLD if cleared else ACCENT_CYAN if can_enter else TEXT_MUTED)
        num = self._font_room.render(f"Room {room['number']}", True, num_col)
        surface.blit(num, (x0, y))

        if cleared:
            score_s = self._font_sm.render(f"{node['score']} pts", True, ACCENT_GOLD)
            surface.blit(score_s, (rect.right - score_s.get_width() - 12, y + 2))

        y += num.get_height() + 3

        # ── title — always real text, styling varies by state ─────────────────
        if cleared or can_enter:
            t_col = TEXT_PRIMARY
        elif locked:
            t_col = TEXT_DIM
        else:
            t_col = (52, 38, 60)
        title = self._font_room.render(room["title"], True, t_col)
        surface.blit(title, (x0, y))
        y += title.get_height() + 5

        # ── concept line ──────────────────────────────────────────────────────
        concept_col = (
            tier_col if (cleared or can_enter) else
            TEXT_MUTED if locked else (32, 18, 28)
        )
        concept = self._font_sm.render(room.get("concept", ""), True, concept_col)
        surface.blit(concept, (x0, y))
        y += concept.get_height() + 6

        pygame.draw.line(surface, BORDER, (x0, y), (rect.right - 12, y), 1)
        y += 8

        # ── teaser ────────────────────────────────────────────────────────────
        teaser_col = (
            TEXT_DIM if (cleared or can_enter) else
            TEXT_MUTED if locked else (38, 22, 32)
        )
        teaser_lines = self._wrap(room.get("teaser", ""), self._font_sm, rect.w - 24)
        for line in teaser_lines[:2]:
            ls = self._font_sm.render(line, True, teaser_col)
            surface.blit(ls, (x0, y))
            y += self._font_sm.get_height() + 2

        # ── status badge ──────────────────────────────────────────────────────
        by = rect.bottom - self._font_btn.get_height() - 12
        if cleared:
            badge_surf = self._font_btn.render("[ MEMORY RECOVERED ]", True, ACCENT_GOLD)
        elif can_enter:
            badge_surf = self._font_btn.render(
                "[  ENTER  ]" if hovered else "[  AVAILABLE  ]",
                True, ACCENT_CYAN if hovered else ACCENT_GREEN,
            )
        elif locked:
            badge_surf = self._font_sm.render(
                "[ LOCKED — complete previous room ]", True, (180, 50, 80)
            )
            by += (self._font_btn.get_height() - self._font_sm.get_height()) // 2
        else:
            badge_surf = self._font_btn.render("[ COMING SOON ]", True, TEXT_MUTED)
        surface.blit(badge_surf, (x0, by))

        # ── memory decay overlay (cleared rooms only) ──────────────────────────
        if cleared:
            decay = self._decays.get(room["id"], 0.0)
            if decay > 0.04:
                seed        = int(self._time * 24 + idx * 37)
                flicker_add = 80 if (seed % 100 < int(decay * 14)) else 0
                alpha       = min(190, int(decay * 52) + flicker_add)
                r, g, b     = BG_DARK
                self._decay_surf.fill((r, g, b, alpha))
                surface.blit(self._decay_surf, rect.topleft)

    def _corrupt_text(self, text: str, room_id: str) -> str:
        """Glitch a room title with random char substitutions that change every ~0.4 s."""
        seed = int(self._time * 2.5) * 7919 + (hash(room_id) & 0xFFFF)
        rng  = random.Random(seed)
        chars = list(text)
        for i in range(len(chars)):
            if chars[i] != ' ' and rng.random() < 0.20:
                chars[i] = rng.choice(_GLITCH_CHARS)
        return ''.join(chars)

    def _draw_fragments_bar(self, surface: pygame.Surface) -> None:
        total   = len(ROOMS)
        dot_r   = 5
        spacing = 18
        total_w = total * (dot_r * 2) + (total - 1) * (spacing - dot_r * 2)
        sx = SCREEN_WIDTH // 2 - total_w // 2
        y  = SCREEN_HEIGHT - 22

        for i, room in enumerate(ROOMS):
            x       = sx + i * spacing
            cleared = self.game.save.is_cleared(room["id"])
            col     = ACCENT_GOLD if cleared else (BORDER if room["available"] else (28, 14, 22))
            pygame.draw.circle(surface, col, (x, y), dot_r, 0 if cleared else 1)

        label = self._font_sm.render("FRAGMENT PROGRESS", True, TEXT_MUTED)
        surface.blit(label, label.get_rect(centerx=SCREEN_WIDTH // 2, y=y + 10))

    def _draw_tooltip(self, surface: pygame.Surface,
                      room: dict, mouse: tuple) -> None:
        if room["available"]:
            available_rooms = [r for r in ROOMS if r["available"]]
            try:
                idx  = available_rooms.index(room)
                prev = available_rooms[idx - 1]["title"] if idx > 0 else None
                status = f"Complete: {prev}" if prev else "AVAILABLE"
            except ValueError:
                status = "COMING SOON"
        else:
            status = "COMING SOON"

        lines = [
            room["title"],
            room.get("concept", ""),
            "",
            room.get("teaser", ""),
            "",
            status,
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
