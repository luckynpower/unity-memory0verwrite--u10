"""
Memory Archive — displays all 8 recovered (and pending) fragment cards.
Accessible from the World Map.  State key: "archive"
"""
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_GOLD,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_HEADER_H = 80
_COLS      = 2
_CARD_W    = 580
_CARD_H    = 105
_CARD_VGAP = 9
# 2 cols of 580px with 20px gap, centred in 1280px screen
_LEFT_X    = (SCREEN_WIDTH - (_COLS * _CARD_W + (_COLS - 1) * 20)) // 2
_CARDS_Y   = 140


class Archive(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_h1   = pygame.font.SysFont("consolas", 24, bold=True)
        self._font_room = pygame.font.SysFont("consolas", 14, bold=True)
        self._font_body = pygame.font.SysFont("consolas", 13)
        self._font_sm   = pygame.font.SysFont("consolas", 11)
        self._font_btn  = pygame.font.SysFont("consolas", 15, bold=True)
        self._font_bar  = pygame.font.SysFont("consolas", 13, bold=True)
        self._btn_hover = False
        self._time      = 0.0

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
            if self._get_btn_rect().collidepoint(event.pos):
                self.game.audio.play("click")
                self.game.sm.transition("rooms")

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        mx, my = pygame.mouse.get_pos()
        self._btn_hover = self._get_btn_rect().collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_bg(surface)
        self._draw_header(surface)
        self._draw_containment_bar(surface)
        self._draw_cards(surface)
        self._draw_nav(surface)
        fx.scanlines(surface, alpha=18)

    def _draw_bg(self, surface: pygame.Surface) -> None:
        dot_col = (24, 32, 50)
        for x in range(0, SCREEN_WIDTH, 30):
            for y in range(_HEADER_H, SCREEN_HEIGHT - 32, 30):
                pygame.draw.circle(surface, dot_col, (x, y), 1)

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER, (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        title = self._font_h1.render("MEMORY ARCHIVE  //  FRAGMENT JOURNAL", True, ACCENT_CYAN)
        surface.blit(title, (28, 22))

        hint = self._font_sm.render("ESC = return to rooms", True, TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 28, 32))

    def _draw_containment_bar(self, surface: pygame.Surface) -> None:
        total   = len(ROOMS)
        cleared = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        pct     = cleared / total

        cx = SCREEN_WIDTH // 2
        y  = _HEADER_H + 12

        if cleared == total:
            status_text = "VIRUS DEFEATED"
            s_col       = ACCENT_GREEN
        elif cleared > 0:
            status_text = f"VIRUS WEAKENED  —  {cleared}/{total} fragments recovered"
            s_col       = ACCENT_ORANGE
        else:
            status_text = "VIRUS ACTIVE  —  no fragments recovered"
            s_col       = ACCENT_RED

        lbl = self._font_bar.render(f"CONTAINMENT: {status_text}", True, s_col)
        surface.blit(lbl, lbl.get_rect(centerx=cx, y=y))

        bar_w = 700
        bar_h = 10
        bar_x = cx - bar_w // 2
        bar_y = y + lbl.get_height() + 5

        pygame.draw.rect(surface, (50, 12, 22), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(surface, ACCENT_GREEN, (bar_x, bar_y, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, BORDER, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)

    def _draw_cards(self, surface: pygame.Surface) -> None:
        for i, room in enumerate(ROOMS):
            col  = i // 4
            row  = i %  4
            x    = _LEFT_X + col * (_CARD_W + 20)
            y    = _CARDS_Y + row * (_CARD_H + _CARD_VGAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self._draw_card(surface, rect, room)

    def _draw_card(self, surface: pygame.Surface,
                   rect: pygame.Rect, room: dict) -> None:
        cleared    = self.game.save.is_cleared(room["id"])
        frag       = room.get("memory_fragment")
        fill_col   = (24, 16, 4) if cleared else BG_PANEL
        border_col = ACCENT_GOLD  if cleared else BORDER

        pygame.draw.rect(surface, fill_col,   rect, border_radius=5)
        pygame.draw.rect(surface, border_col, rect, 1, border_radius=5)

        x0 = rect.x + 12
        y  = rect.y + 9

        header_col = ACCENT_GOLD if cleared else TEXT_DIM
        header = self._font_room.render(
            f"Room {room['number']}  //  {room['title'].upper()}", True, header_col
        )
        surface.blit(header, (x0, y))
        y += header.get_height() + 4

        pygame.draw.line(surface, border_col, (x0, y), (rect.right - 12, y), 1)
        y += 7

        if cleared and frag:
            lines = self._wrap(frag, self._font_body, rect.w - 26)
            for line in lines[:3]:
                ls = self._font_body.render(line, True, TEXT_PRIMARY)
                surface.blit(ls, (x0, y))
                y += self._font_body.get_height() + 3
        elif cleared:
            ph = self._font_body.render("Fragment recovered. Full recall pending.", True, TEXT_DIM)
            surface.blit(ph, (x0, y))
        else:
            ph = self._font_body.render("[ MEMORY NOT YET RECOVERED ]", True, TEXT_MUTED)
            surface.blit(ph, (x0, y))

        by    = rect.bottom - self._font_sm.get_height() - 7
        bx    = rect.right  - 12
        badge = (
            self._font_sm.render("RECOVERED", True, ACCENT_GOLD) if cleared else
            self._font_sm.render("LOCKED",    True, (55, 30, 45))
        )
        surface.blit(badge, (bx - badge.get_width(), by))

    def _draw_nav(self, surface: pygame.Surface) -> None:
        r    = self._get_btn_rect()
        col  = ACCENT_CYAN if self._btn_hover else TEXT_DIM
        bc   = ACCENT_CYAN if self._btn_hover else BORDER
        fill = (0, 30, 52) if self._btn_hover else BG_PANEL
        pygame.draw.rect(surface, fill, r, border_radius=4)
        pygame.draw.rect(surface, bc,   r, 2, border_radius=4)
        lbl = self._font_btn.render("<  RETURN TO ROOMS", True, col)
        surface.blit(lbl, lbl.get_rect(center=r.center))

    def _get_btn_rect(self) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 50, 320, 38)

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
