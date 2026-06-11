"""
Context scene — mission briefing shown between room selection and gameplay.
Flow: Rooms screen  →  Context  →  Room Game
"""
import math
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS, ROOM_TIMER_SECONDS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_ORANGE, ACCENT_GOLD,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_CHARS_PER_SEC = 55.0
_HEADER_H      = 72
_CONTENT_W     = 700

_TIER_LABEL = {
    1: "TIER 1  ·  ENTRY POINT",
    2: "TIER 2  ·  TECHNICAL",
    3: "TIER 3  ·  HACKER MINDSET",
    4: "TIER 4  ·  DEEP DIVE",
}


class Context(BaseScene):
    """Pre-room narrative / mission briefing screen."""

    def __init__(self, game):
        super().__init__(game)
        self._font_tag   = pygame.font.SysFont("consolas", 13)
        self._font_title = pygame.font.SysFont("consolas", 26, bold=True)
        self._font_body  = pygame.font.SysFont("consolas", 16)
        self._font_sm    = pygame.font.SysFont("consolas", 13)
        self._font_btn   = pygame.font.SysFont("consolas", 20, bold=True)
        self._font_hint  = pygame.font.SysFont("consolas", 12)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self, room_id: str = "", **kwargs) -> None:
        self._room_id   = room_id
        self._room      = next((r for r in ROOMS if r["id"] == room_id), None)
        self._narrative = (self._room or {}).get(
            "narrative", "Initiating room sequence. Stand by."
        )
        self._char_idx  = 0.0
        self._skip      = False
        self._btn_hover = False
        self._time      = 0.0
        self._is_replay = self.game.save.is_cleared(room_id)
        self._prev_score = self.game.save.get_score(room_id) if self._is_replay else 0

    def on_exit(self) -> None:
        pass

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.audio.play("click")
                self.game.sm.transition("rooms")
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._advance()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._skip and self._get_btn_rect().collidepoint(event.pos):
                self.game.audio.play("click")
                self._start_room()

    def _advance(self) -> None:
        if not self._skip:
            self._skip = True           # first press: reveal full text
        else:
            self.game.audio.play("click")
            self._start_room()

    def _start_room(self) -> None:
        self.game.audio.play("room_enter")
        self.game.sm.transition(
            "room_game",
            room_id=self._room_id,
            timer_seconds=ROOM_TIMER_SECONDS,
        )

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        if not self._skip:
            self._char_idx = min(
                len(self._narrative),
                self._char_idx + _CHARS_PER_SEC * dt,
            )
            if self._char_idx >= len(self._narrative):
                self._skip = True
        mx, my = pygame.mouse.get_pos()
        self._btn_hover = self._get_btn_rect().collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_bg_grid(surface)
        self._draw_header(surface)
        self._draw_content(surface)
        if self._skip:
            self._draw_button(surface)
        self._draw_footer(surface)
        fx.scanlines(surface, alpha=18)

    def _draw_bg_grid(self, surface: pygame.Surface) -> None:
        dot_col = (28, 36, 52)
        for x in range(0, SCREEN_WIDTH, 30):
            for y in range(_HEADER_H, SCREEN_HEIGHT, 30):
                pygame.draw.circle(surface, dot_col, (x, y), 1)

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, ACCENT_CYAN,
                         (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        if self._room:
            tag_label = "REPLAY MISSION" if self._is_replay else "MISSION BRIEFING"
            tag = self._font_tag.render(
                f"ROOM {self._room['number']}  //  {tag_label}", True, TEXT_MUTED
            )
            surface.blit(tag, (24, 10))
            title = self._font_title.render(
                self._room["title"].upper(), True, ACCENT_CYAN
            )
            surface.blit(title, (24, 10 + tag.get_height() + 4))

        hint = self._font_hint.render(
            "ESC = back  |  SPACE = skip  |  ENTER = begin", True, TEXT_MUTED
        )
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 24,
                            (_HEADER_H - hint.get_height()) // 2))

    def _draw_content(self, surface: pygame.Surface) -> None:
        cx  = SCREEN_WIDTH // 2
        bx  = cx - _CONTENT_W // 2
        y   = _HEADER_H + 36

        # Concept badge + optional replay score
        if self._room:
            concept = self._room.get("concept", "").upper()
            badge_s = self._font_sm.render(f"  [ {concept} ]  ", True, ACCENT_ORANGE)
            badge_r = pygame.Rect(bx, y, badge_s.get_width() + 4, badge_s.get_height() + 6)
            pygame.draw.rect(surface, (35, 18, 0), badge_r, border_radius=3)
            pygame.draw.rect(surface, ACCENT_ORANGE, badge_r, 1, border_radius=3)
            surface.blit(badge_s, (bx + 2, y + 3))
            if self._is_replay:
                replay_s = self._font_sm.render(
                    f"Previous score:  {self._prev_score} pts", True, ACCENT_GOLD
                )
                surface.blit(replay_s, (bx + badge_r.w + 18, y + 3))
            y += badge_r.h + 24

        # Narrative text box
        visible = (self._narrative if self._skip
                   else self._narrative[:int(self._char_idx)])
        lines   = self._wrap(visible, self._font_body, _CONTENT_W - 32)

        lh     = self._font_body.get_height() + 5
        box_h  = max(140, len(lines) * lh + 38)
        box_r  = pygame.Rect(bx, y, _CONTENT_W, box_h)
        pygame.draw.rect(surface, BG_PANEL, box_r, border_radius=6)
        pygame.draw.rect(surface, ACCENT_CYAN, box_r, 1, border_radius=6)
        pygame.draw.rect(surface, ACCENT_CYAN,
                         pygame.Rect(bx, y + 10, 3, box_h - 20), border_radius=2)

        ty = y + 20
        for line in lines:
            ls = self._font_body.render(line, True, TEXT_PRIMARY)
            surface.blit(ls, (bx + 18, ty))
            ty += lh

        # Blinking cursor while typing
        if not self._skip and int(self._char_idx) < len(self._narrative):
            if int(self._time * 2) % 2 == 0:
                csr   = self._font_body.render("█", True, ACCENT_CYAN)
                last  = lines[-1] if lines else ""
                cx_p  = bx + 18 + self._font_body.size(last)[0] + 2
                surface.blit(csr, (cx_p, ty - lh))

        y += box_h + 18

        # Sub-hint
        if not self._skip:
            sh = self._font_hint.render(
                "Press SPACE to reveal full briefing.", True, TEXT_MUTED
            )
        else:
            sh = self._font_hint.render(
                "Press ENTER or click ENTER ROOM to begin.", True, TEXT_DIM
            )
        surface.blit(sh, sh.get_rect(centerx=cx, y=y))

    def _draw_button(self, surface: pygame.Surface) -> None:
        r     = self._get_btn_rect()
        t     = self._time
        pulse = 0.60 + 0.40 * abs(math.sin(t * 2.4))
        r0, g0, b0 = BORDER
        ra, ga, ba = ACCENT_GREEN
        bc = (
            ACCENT_GREEN if self._btn_hover else
            (int(r0 + (ra - r0) * pulse),
             int(g0 + (ga - g0) * pulse),
             int(b0 + (ba - b0) * pulse))
        )
        fill = (0, 55, 44) if self._btn_hover else BG_PANEL
        col  = ACCENT_GREEN if self._btn_hover else TEXT_PRIMARY
        pygame.draw.rect(surface, fill, r, border_radius=5)
        pygame.draw.rect(surface, bc,   r, 2, border_radius=5)
        label = "REPLAY ROOM  >" if self._is_replay else "ENTER ROOM  >"
        lbl = self._font_btn.render(label, True, col)
        surface.blit(lbl, lbl.get_rect(center=r.center))

    def _draw_footer(self, surface: pygame.Surface) -> None:
        fy  = SCREEN_HEIGHT - 30
        pygame.draw.line(surface, BORDER,
                         (0, fy - 6), (SCREEN_WIDTH, fy - 6), 1)
        tier_str = _TIER_LABEL.get((self._room or {}).get("tier", 0), "")
        ts = self._font_hint.render(tier_str, True, TEXT_MUTED)
        surface.blit(ts, ts.get_rect(centerx=SCREEN_WIDTH // 2, y=fy))

    def _get_btn_rect(self) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 120, 340, 50)

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
