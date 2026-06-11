"""
Memory Archive — the fragment journal.
Shows all 8 rooms: recovered fragments in detail, locked ones with teaser.
State key: "archive"
"""
import math
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_GOLD,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_HEADER_H  = 88
_COLS      = 2
_CARD_W    = 574
_CARD_H    = 126
_CARD_VGAP = 9
_CARDS_TOP = _HEADER_H + 46        # first card row y
_COL_GAP   = 20
_LEFT_X    = (SCREEN_WIDTH - (_COLS * _CARD_W + _COL_GAP)) // 2   # = 56

# Accent stripe width on left side of each card
_STRIPE_W  = 4

# Tier accent colours (shared with world_map)
_TIER_COLOR = {1: ACCENT_GREEN, 2: ACCENT_CYAN, 3: ACCENT_ORANGE, 4: ACCENT_RED}


class Archive(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_h1    = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_title = pygame.font.SysFont("consolas", 14, bold=True)
        self._font_sub   = pygame.font.SysFont("consolas", 12, bold=True)
        self._font_body  = pygame.font.SysFont("consolas", 12)
        self._font_sm    = pygame.font.SysFont("consolas", 11)
        self._font_btn   = pygame.font.SysFont("consolas", 15, bold=True)
        self._font_bar   = pygame.font.SysFont("consolas", 13, bold=True)
        self._btn_hover  = False
        self._time       = 0.0

    def on_enter(self, **kwargs) -> None:
        self._time      = 0.0
        self._btn_hover = False

    def on_exit(self) -> None:
        pass

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.audio.play("click")
            self.game.sm.transition("rooms")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_rect().collidepoint(event.pos):
                self.game.audio.play("click")
                self.game.sm.transition("rooms")

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        mx, my = pygame.mouse.get_pos()
        self._btn_hover = self._btn_rect().collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_dots(surface)
        self._draw_header(surface)
        self._draw_containment_bar(surface)
        self._draw_cards(surface)
        self._draw_nav(surface)
        fx.scanlines(surface, alpha=18)

    # ── background dots ───────────────────────────────────────────────────────

    def _draw_dots(self, surface: pygame.Surface) -> None:
        col = (22, 30, 48)
        for x in range(0, SCREEN_WIDTH, 28):
            for y in range(_HEADER_H, SCREEN_HEIGHT - 32, 28):
                pygame.draw.circle(surface, col, (x, y), 1)

    # ── header ────────────────────────────────────────────────────────────────

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER, (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        title = self._font_h1.render("MEMORY ARCHIVE  //  FRAGMENT JOURNAL", True, ACCENT_CYAN)
        surface.blit(title, (28, 20))

        cleared = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        sub = self._font_sm.render(
            f"{cleared} of {len(ROOMS)} memory fragments recovered", True, TEXT_DIM
        )
        surface.blit(sub, (28, 20 + title.get_height() + 4))

        hint = self._font_sm.render("ESC  =  return to rooms", True, TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 28, 36))

    # ── containment bar ───────────────────────────────────────────────────────

    def _draw_containment_bar(self, surface: pygame.Surface) -> None:
        total   = len(ROOMS)
        cleared = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        pct     = cleared / total

        cx = SCREEN_WIDTH // 2
        y  = _HEADER_H + 8

        if cleared == total:
            label, col = "VIRUS DEFEATED — ALL FRAGMENTS RESTORED", ACCENT_GREEN
        elif cleared > 0:
            label, col = f"VIRUS WEAKENED  —  {cleared}/{total} fragments", ACCENT_ORANGE
        else:
            label, col = "VIRUS ACTIVE  —  no fragments recovered", ACCENT_RED

        lbl = self._font_bar.render(f"CONTAINMENT: {label}", True, col)
        surface.blit(lbl, lbl.get_rect(centerx=cx, y=y))

        bar_w, bar_h = 700, 8
        bar_x = cx - bar_w // 2
        bar_y = y + lbl.get_height() + 5
        pygame.draw.rect(surface, (44, 10, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(surface, ACCENT_GREEN, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, BORDER, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

    # ── cards ─────────────────────────────────────────────────────────────────

    def _draw_cards(self, surface: pygame.Surface) -> None:
        for i, room in enumerate(ROOMS):
            col  = i // 4
            row  = i %  4
            x    = _LEFT_X + col * (_CARD_W + _COL_GAP)
            y    = _CARDS_TOP + row * (_CARD_H + _CARD_VGAP)
            self._draw_card(surface, pygame.Rect(x, y, _CARD_W, _CARD_H), room, i + 1)

    def _draw_card(self, surface: pygame.Surface,
                   rect: pygame.Rect, room: dict, frag_num: int) -> None:
        cleared    = self.game.save.is_cleared(room["id"])
        tier_col   = _TIER_COLOR.get(room["tier"], TEXT_DIM)
        frag_title = room.get("fragment_title", f"Fragment {frag_num}")
        frag_text  = room.get("memory_fragment") or ""
        frag_tease = room.get("fragment_teaser", "")

        if cleared:
            fill_col   = (18, 14, 4)
            border_col = ACCENT_GOLD
            stripe_col = ACCENT_GOLD
        else:
            fill_col   = (14, 10, 18)
            border_col = BORDER
            stripe_col = (38, 22, 50)

        pygame.draw.rect(surface, fill_col,   rect, border_radius=5)
        pygame.draw.rect(surface, border_col, rect, 1, border_radius=5)
        # Left accent stripe
        stripe = pygame.Rect(rect.x + 1, rect.y + 6, _STRIPE_W, rect.h - 12)
        pygame.draw.rect(surface, stripe_col, stripe, border_radius=2)

        pad   = 14
        x0    = rect.x + pad + _STRIPE_W + 4
        avail = rect.w - x0 + rect.x - pad        # text area width

        if cleared:
            self._draw_card_cleared(surface, rect, x0, avail, frag_num,
                                    frag_title, frag_text, room, tier_col)
        else:
            self._draw_card_locked(surface, rect, x0, avail, frag_num,
                                   frag_tease, room)

    def _draw_card_cleared(self, surface, rect, x0, avail,
                            frag_num, frag_title, frag_text, room, tier_col):
        y = rect.y + 8

        # Fragment number tag + title
        tag = self._font_sub.render(f"FRAGMENT  #{frag_num:02d}", True, ACCENT_GOLD)
        surface.blit(tag, (x0, y))

        # Right-aligned room info
        room_s = self._font_sm.render(
            f"Room {room['number']}  ·  {room['title']}", True, TEXT_DIM
        )
        surface.blit(room_s, (rect.right - room_s.get_width() - 12, y + 2))
        y += tag.get_height() + 3

        # Fragment title
        ft = self._font_title.render(frag_title.upper(), True, ACCENT_GOLD)
        surface.blit(ft, (x0, y))

        # Tier badge right-aligned
        tier_s = self._font_sm.render(f"Tier {room['tier']}", True, tier_col)
        surface.blit(tier_s, (rect.right - tier_s.get_width() - 12,
                               y + (ft.get_height() - tier_s.get_height()) // 2))
        y += ft.get_height() + 5

        pygame.draw.line(surface, (60, 44, 10),
                         (x0, y), (rect.right - 12, y), 1)
        y += 6

        # Story text — wrap to 2 lines maximum
        lines = self._wrap(frag_text, self._font_body, avail - 12)
        for line in lines[:2]:
            ls = self._font_body.render(line, True, TEXT_PRIMARY)
            surface.blit(ls, (x0, y))
            y += self._font_body.get_height() + 2

        if len(lines) > 2:
            cont = self._font_sm.render("— continued —", True, TEXT_MUTED)
            surface.blit(cont, (x0, y))

        # RECOVERED badge bottom-right
        badge = self._font_sm.render("MEMORY RECOVERED", True, ACCENT_GOLD)
        bx = rect.right - badge.get_width() - 12
        by = rect.bottom - badge.get_height() - 7
        surface.blit(badge, (bx, by))

    def _draw_card_locked(self, surface, rect, x0, avail,
                           frag_num, frag_tease, room):
        y = rect.y + 8

        # Fragment number
        tag = self._font_sub.render(f"FRAGMENT  #{frag_num:02d}", True, TEXT_MUTED)
        surface.blit(tag, (x0, y))
        y += tag.get_height() + 4

        # Obscured title (shown as blocks)
        obscured = "█" * min(18, max(8, len(room.get("fragment_title", "")) + 2))
        ob_s = self._font_title.render(obscured, True, (44, 28, 58))
        surface.blit(ob_s, (x0, y))
        y += ob_s.get_height() + 5

        pygame.draw.line(surface, (44, 28, 58),
                         (x0, y), (rect.right - 12, y), 1)
        y += 6

        # Teaser text
        if frag_tease:
            lines = self._wrap(f'"{frag_tease}"', self._font_body, avail - 12)
            for line in lines[:1]:
                ls = self._font_body.render(line, True, (80, 55, 90))
                surface.blit(ls, (x0, y))
                y += self._font_body.get_height() + 2

        # Recovery hint
        hint = self._font_sm.render(
            f"Recover in:  {room['title']}", True, TEXT_MUTED
        )
        surface.blit(hint, (x0, rect.bottom - hint.get_height() - 7))

        # LOCKED badge bottom-right
        badge = self._font_sm.render("LOCKED", True, (70, 38, 80))
        surface.blit(badge, (rect.right - badge.get_width() - 12,
                             rect.bottom - badge.get_height() - 7))

    # ── nav button ────────────────────────────────────────────────────────────

    def _draw_nav(self, surface: pygame.Surface) -> None:
        r    = self._btn_rect()
        col  = ACCENT_CYAN if self._btn_hover else TEXT_DIM
        bc   = ACCENT_CYAN if self._btn_hover else BORDER
        fill = (0, 30, 52) if self._btn_hover else BG_PANEL
        pygame.draw.rect(surface, fill, r, border_radius=4)
        pygame.draw.rect(surface, bc,   r, 2, border_radius=4)
        lbl = self._font_btn.render("<  RETURN TO ROOMS", True, col)
        surface.blit(lbl, lbl.get_rect(center=r.center))

    def _btn_rect(self) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 46, 320, 36)

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
