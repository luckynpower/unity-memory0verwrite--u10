"""
Room-result screen — shown after every room completion.
Receives: room_id, score, max_score via transition kwargs.
Looks up the memory_fragment string from ROOMS in settings.
"""
import math
import pygame
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_DISPLAY_SECONDS = 0.0   # no auto-advance; player must click


def _room_by_id(room_id: str) -> dict | None:
    for r in ROOMS:
        if r["id"] == room_id:
            return r
    return None


class RoomResult(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_head  = pygame.font.SysFont("consolas", 26, bold=True)
        self._font_sub   = pygame.font.SysFont("consolas", 18, bold=True)
        self._font_body  = pygame.font.SysFont("consolas", 15)
        self._font_sm    = pygame.font.SysFont("consolas", 13)
        self._font_btn   = pygame.font.SysFont("consolas", 18, bold=True)

    def on_enter(self, room_id: str = "", score: int = 0,
                 max_score: int = 100, **kwargs) -> None:
        self._room_id   = room_id
        self._score     = score
        self._max_score = max_score
        self._room      = _room_by_id(room_id)
        self._time      = 0.0
        self._flash_t   = 0.0
        self._revealed  = False
        self._btn_hover = False

        # Check if this completion finishes all available rooms
        available = [r for r in ROOMS if r["available"]]
        self._is_final = bool(available) and all(
            self.game.save.is_cleared(r["id"]) for r in available
        )
        self._cleared_count = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))

        self._fanfare_played = False
        self.game.audio.stop_ambient()

    def on_exit(self) -> None:
        self.game.audio.start_ambient()

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._get_btn_rect().collidepoint(event.pos):
                self.game.audio.play("click")
                self._continue()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.game.audio.play("click")
            self._continue()

    def _continue(self) -> None:
        if self._is_final:
            self.game.sm.transition("ending")
        else:
            self.game.sm.transition("rooms")

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time   += dt
        self._flash_t = min(1.0, self._flash_t + dt * 1.6)

        if self._time > 0.6 and not self._fanfare_played:
            self.game.audio.play("fragment")
            self._fanfare_played = True

        if self._time > 1.2:
            self._revealed = True

        mx, my = pygame.mouse.get_pos()
        self._btn_hover = self._get_btn_rect().collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_bg_pulse(surface)
        self._draw_panel(surface)
        self._draw_button(surface)

    def _draw_bg_pulse(self, surface: pygame.Surface) -> None:
        """Green-tinted radial pulse that fades out."""
        alpha = int(max(0, 120 * (1.0 - self._flash_t)))
        if alpha == 0:
            return
        pulse = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(
            pulse, (0, 200, 80, alpha),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            int(100 + 500 * self._flash_t),
        )
        surface.blit(pulse, (0, 0))

    def _draw_panel(self, surface: pygame.Surface) -> None:
        cx = SCREEN_WIDTH // 2
        panel = pygame.Rect(cx - 420, 60, 840, SCREEN_HEIGHT - 160)
        pygame.draw.rect(surface, BG_MID, panel, border_radius=8)
        pygame.draw.rect(surface, ACCENT_GREEN, panel, 2, border_radius=8)

        y = panel.y + 28

        # ── headline ─────────────────────────────────────────────────────────
        head = self._font_head.render("MEMORY FRAGMENT RECOVERED", True, ACCENT_GREEN)
        surface.blit(head, head.get_rect(centerx=cx, y=y))
        y += head.get_height() + 6

        if self._room:
            sub = self._font_sub.render(
                f"Room {self._room['number']}  —  {self._room['title']}",
                True, ACCENT_CYAN,
            )
            surface.blit(sub, sub.get_rect(centerx=cx, y=y))
            y += sub.get_height() + 4

        pygame.draw.line(surface, BORDER, (panel.x + 30, y + 8), (panel.right - 30, y + 8), 1)
        y += 24

        # ── score ─────────────────────────────────────────────────────────────
        pct   = self._score / max(1, self._max_score)
        s_col = ACCENT_GREEN if pct >= 0.8 else (ACCENT_ORANGE if pct >= 0.4 else ACCENT_RED)
        score_s = self._font_sub.render(
            f"Score:  {self._score}  /  {self._max_score}", True, s_col
        )
        surface.blit(score_s, score_s.get_rect(centerx=cx, y=y))
        y += score_s.get_height() + 6

        # Score bar
        bar_w = 500
        bar_h = 10
        bar_x = cx - bar_w // 2
        pygame.draw.rect(surface, BG_PANEL, (bar_x, y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(surface, s_col, (bar_x, y, fill_w, bar_h), border_radius=4)
        y += bar_h + 18

        # ── fragment tracker ──────────────────────────────────────────────────
        total     = len(ROOMS)
        cleared   = self._cleared_count
        dot_r     = 6
        dot_space = 22
        dots_w    = (total - 1) * dot_space + dot_r * 2
        dx        = cx - dots_w // 2

        for j, room in enumerate(ROOMS):
            cx_j        = dx + j * dot_space
            is_cleared  = self.game.save.is_cleared(room["id"])
            # highlight the room we just cleared with a larger ring
            is_this     = room["id"] == self._room_id
            col_dot     = ACCENT_GOLD if is_cleared else (BORDER if room["available"] else BG_PANEL)
            pygame.draw.circle(surface, col_dot, (cx_j, y + dot_r), dot_r, 0 if is_cleared else 1)
            if is_this:
                pygame.draw.circle(surface, ACCENT_GREEN, (cx_j, y + dot_r), dot_r + 3, 1)

        y += dot_r * 2 + 8

        frag_line = self._font_sm.render(
            f"Fragments recovered:  {cleared} / {total}", True,
            ACCENT_GOLD if cleared == total else TEXT_DIM,
        )
        surface.blit(frag_line, frag_line.get_rect(centerx=cx, y=y))
        y += frag_line.get_height() + 14

        # ── virus weakening indicator ─────────────────────────────────────────
        before_pct = (total - (cleared - 1)) / total
        after_pct  = (total - cleared) / total
        v_label = self._font_sm.render(
            f"VIRUS STRENGTH:  {int(before_pct * 100)}%  →  {int(after_pct * 100)}%",
            True, ACCENT_ORANGE,
        )
        surface.blit(v_label, v_label.get_rect(centerx=cx, y=y))
        y += v_label.get_height() + 6

        vbar_w = 380
        vbar_h = 8
        vbar_x = cx - vbar_w // 2
        pygame.draw.rect(surface, BG_PANEL, (vbar_x, y, vbar_w, vbar_h), border_radius=3)
        vfill_w = int(vbar_w * after_pct)
        if vfill_w > 0:
            pygame.draw.rect(surface, ACCENT_RED, (vbar_x, y, vfill_w, vbar_h), border_radius=3)
        pygame.draw.rect(surface, (40, 18, 30), (vbar_x, y, vbar_w, vbar_h), 1, border_radius=3)
        y += vbar_h + 20

        # ── memory fragment ───────────────────────────────────────────────────
        frag_label = self._font_sm.render("[ MEMORY FRAGMENT ]", True, TEXT_MUTED)
        surface.blit(frag_label, frag_label.get_rect(centerx=cx, y=y))
        y += frag_label.get_height() + 8

        frag_text = (
            (self._room or {}).get("memory_fragment") or
            "A fragment of memory reassembles, faint but real."
        )
        if self._revealed:
            frag_w = panel.w - 80
            lines  = self._wrap(frag_text, self._font_body, frag_w)
            # Draw fragment box
            box_h  = len(lines) * (self._font_body.get_height() + 4) + 24
            box    = pygame.Rect(cx - frag_w // 2 - 12, y, frag_w + 24, box_h)
            pygame.draw.rect(surface, BG_PANEL, box, border_radius=6)
            pygame.draw.rect(surface, ACCENT_CYAN, box, 1, border_radius=6)
            ty = y + 12
            for line in lines:
                ls = self._font_body.render(line, True, TEXT_PRIMARY)
                surface.blit(ls, ls.get_rect(centerx=cx, y=ty))
                ty += self._font_body.get_height() + 4
        else:
            placeholder = self._font_body.render(
                "Recovering fragment" + "." * (int(self._time * 3) % 4),
                True, TEXT_MUTED,
            )
            surface.blit(placeholder, placeholder.get_rect(centerx=cx, y=y))

    def _draw_button(self, surface: pygame.Surface) -> None:
        import math
        r    = self._get_btn_rect()
        if self._is_final:
            pulse = 0.60 + 0.40 * abs(math.sin(self._time * 2.2))
            r0, g0, b0 = BORDER
            ra, ga, ba = ACCENT_GREEN
            bc = (
                ACCENT_GREEN if self._btn_hover else
                (int(r0 + (ra-r0)*pulse), int(g0 + (ga-g0)*pulse), int(b0 + (ba-b0)*pulse))
            )
            fill  = (0, 55, 28) if self._btn_hover else BG_PANEL
            col   = ACCENT_GREEN
            label = "CONTINUE TO ENDING  >"
        else:
            col   = ACCENT_GREEN if self._btn_hover else TEXT_DIM
            bc    = ACCENT_GREEN if self._btn_hover else BORDER
            fill  = (0, 55, 28) if self._btn_hover else BG_PANEL
            label = "RETURN TO ROOMS  >"
        pygame.draw.rect(surface, fill, r, border_radius=4)
        pygame.draw.rect(surface, bc,   r, 2, border_radius=4)
        lbl = self._font_btn.render(label, True, col)
        surface.blit(lbl, lbl.get_rect(center=r.center))

    def _get_btn_rect(self) -> pygame.Rect:
        w = 420 if getattr(self, "_is_final", False) else 360
        return pygame.Rect(SCREEN_WIDTH // 2 - w // 2, SCREEN_HEIGHT - 90, w, 44)

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
