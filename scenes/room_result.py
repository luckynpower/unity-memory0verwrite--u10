"""
Room-result screen — shown after every room completion.
Receives: room_id, score, max_score, is_first_clear via transition kwargs.
"""
import math
import pygame
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_GOLD,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)


def _room_by_id(room_id: str) -> dict | None:
    for r in ROOMS:
        if r["id"] == room_id:
            return r
    return None


class RoomResult(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_head = pygame.font.SysFont("consolas", 26, bold=True)
        self._font_sub  = pygame.font.SysFont("consolas", 18, bold=True)
        self._font_body = pygame.font.SysFont("consolas", 15)
        self._font_sm   = pygame.font.SysFont("consolas", 13)
        self._font_btn  = pygame.font.SysFont("consolas", 17, bold=True)
        self._asurf     = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def on_enter(self, room_id: str = "", score: int = 0,
                 max_score: int = 100, is_first_clear: bool = False, **kwargs) -> None:
        self._room_id      = room_id
        self._score        = score
        self._max_score    = max_score
        self._is_first_clear = is_first_clear
        self._room         = _room_by_id(room_id)
        self._time         = 0.0
        self._flash_t      = 0.0
        self._revealed     = False
        self._fanfare_played = False

        # Check progression state (save already updated by room_game before transition)
        available          = [r for r in ROOMS if r["available"]]
        self._is_final     = bool(available) and all(
            self.game.save.is_cleared(r["id"]) for r in available
        )
        self._cleared_count = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        self._newly_unlocked = self._find_newly_unlocked()

        self._build_buttons()
        self.game.audio.stop_ambient()

    def on_exit(self) -> None:
        self.game.audio.start_ambient()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _find_newly_unlocked(self) -> dict | None:
        """Return the next available room that just became accessible, or None."""
        if not self._is_first_clear:
            return None
        available = [r for r in ROOMS if r["available"]]
        try:
            idx = next(i for i, r in enumerate(available) if r["id"] == self._room_id)
        except StopIteration:
            return None
        nxt = idx + 1
        return available[nxt] if nxt < len(available) else None

    def _build_buttons(self) -> None:
        cx    = SCREEN_WIDTH // 2
        y     = SCREEN_HEIGHT - 84
        bw    = 200
        gap   = 20
        bx    = cx - (3 * bw + 2 * gap) // 2
        self._btns = [
            {"label": "CONTINUE JOURNEY", "key": "continue", "col": ACCENT_GREEN,
             "rect": pygame.Rect(bx,              y, bw, 42)},
            {"label": "REPLAY ROOM",       "key": "replay",   "col": ACCENT_CYAN,
             "rect": pygame.Rect(bx + bw + gap,   y, bw, 42)},
            {"label": "VIEW ARCHIVE",      "key": "archive",  "col": TEXT_DIM,
             "rect": pygame.Rect(bx + 2*(bw+gap), y, bw, 42)},
        ]
        for btn in self._btns:
            btn["hover"] = False

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self._btns:
                if btn["rect"].collidepoint(event.pos):
                    self.game.audio.play("click")
                    self._activate(btn["key"])
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.game.audio.play("click")
                self._activate("continue")
            elif event.key == pygame.K_ESCAPE:
                self.game.audio.play("click")
                self._activate("continue")

    def _activate(self, key: str) -> None:
        if key == "continue":
            self.game.sm.transition("rooms")
        elif key == "replay":
            self.game.sm.transition("context", room_id=self._room_id)
        elif key == "archive":
            self.game.sm.transition("archive")

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time    += dt
        self._flash_t  = min(1.0, self._flash_t + dt * 1.6)

        if self._time > 0.6 and not self._fanfare_played:
            self.game.audio.play("fragment")
            self._fanfare_played = True
        if self._time > 1.2:
            self._revealed = True

        mx, my = pygame.mouse.get_pos()
        for btn in self._btns:
            btn["hover"] = btn["rect"].collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_bg_pulse(surface)
        self._draw_panel(surface)
        self._draw_buttons(surface)

    def _draw_bg_pulse(self, surface: pygame.Surface) -> None:
        alpha = int(max(0, 120 * (1.0 - self._flash_t)))
        if alpha == 0:
            return
        self._asurf.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self._asurf, (0, 200, 80, alpha),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            int(100 + 500 * self._flash_t),
        )
        surface.blit(self._asurf, (0, 0))

    def _draw_panel(self, surface: pygame.Surface) -> None:
        cx    = SCREEN_WIDTH // 2
        panel = pygame.Rect(cx - 420, 52, 840, SCREEN_HEIGHT - 150)
        border_col = ACCENT_GOLD if self._is_final else ACCENT_GREEN
        pygame.draw.rect(surface, BG_MID,      panel, border_radius=8)
        pygame.draw.rect(surface, border_col,  panel, 2, border_radius=8)

        y = panel.y + 24

        # ── headline ─────────────────────────────────────────────────────────
        if self._is_final:
            headline_text = "FINAL FRAGMENT RECOVERED"
            headline_col  = ACCENT_GOLD
        else:
            headline_text = "MEMORY FRAGMENT RECOVERED"
            headline_col  = ACCENT_GREEN
        head = self._font_head.render(headline_text, True, headline_col)
        surface.blit(head, head.get_rect(centerx=cx, y=y))
        y += head.get_height() + 5

        if self._is_final:
            sub = self._font_sub.render(
                "ALL FRAGMENTS RECOVERED  —  VIRUS DEFEATED",
                True, ACCENT_GOLD,
            )
        elif self._room:
            sub = self._font_sub.render(
                f"Room {self._room['number']}  —  {self._room['title']}",
                True, ACCENT_CYAN,
            )
        else:
            sub = None
        if sub:
            surface.blit(sub, sub.get_rect(centerx=cx, y=y))
            y += sub.get_height() + 4

        pygame.draw.line(surface, BORDER, (panel.x + 30, y + 6), (panel.right - 30, y + 6), 1)
        y += 20

        # ── score ─────────────────────────────────────────────────────────────
        pct   = self._score / max(1, self._max_score)
        s_col = ACCENT_GREEN if pct >= 0.8 else (ACCENT_ORANGE if pct >= 0.4 else ACCENT_RED)
        score_s = self._font_sub.render(
            f"Score:  {self._score}  /  {self._max_score}", True, s_col
        )
        surface.blit(score_s, score_s.get_rect(centerx=cx, y=y))
        y += score_s.get_height() + 5

        bar_w = 500
        bar_h = 10
        bar_x = cx - bar_w // 2
        pygame.draw.rect(surface, BG_PANEL, (bar_x, y, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            pygame.draw.rect(surface, s_col, (bar_x, y, fill_w, bar_h), border_radius=4)
        y += bar_h + 16

        # ── fragment tracker dots ─────────────────────────────────────────────
        total     = len(ROOMS)
        cleared   = self._cleared_count
        dot_r     = 6
        dot_space = 22
        dots_w    = (total - 1) * dot_space + dot_r * 2
        dx        = cx - dots_w // 2

        for j, room in enumerate(ROOMS):
            cxj         = dx + j * dot_space
            is_cleared  = self.game.save.is_cleared(room["id"])
            is_this     = room["id"] == self._room_id
            dot_col     = ACCENT_GOLD if is_cleared else (BORDER if room["available"] else BG_PANEL)
            pygame.draw.circle(surface, dot_col, (cxj, y + dot_r), dot_r, 0 if is_cleared else 1)
            if is_this:
                pygame.draw.circle(surface, ACCENT_GREEN, (cxj, y + dot_r), dot_r + 3, 1)

        y += dot_r * 2 + 7

        frag_line = self._font_sm.render(
            f"Fragments recovered:  {cleared} / {total}", True,
            ACCENT_GOLD if cleared == total else TEXT_DIM,
        )
        surface.blit(frag_line, frag_line.get_rect(centerx=cx, y=y))
        y += frag_line.get_height() + 12

        # ── virus weakening indicator ─────────────────────────────────────────
        before_pct = (total - max(0, cleared - 1)) / total
        after_pct  = max(0.0, (total - cleared) / total)
        v_label = self._font_sm.render(
            f"VIRUS STRENGTH:  {int(before_pct * 100)}%  →  {int(after_pct * 100)}%",
            True, ACCENT_ORANGE,
        )
        surface.blit(v_label, v_label.get_rect(centerx=cx, y=y))
        y += v_label.get_height() + 5

        vbar_w = 380
        vbar_h = 8
        vbar_x = cx - vbar_w // 2
        pygame.draw.rect(surface, BG_PANEL, (vbar_x, y, vbar_w, vbar_h), border_radius=3)
        vfill_w = int(vbar_w * after_pct)
        if vfill_w > 0:
            pygame.draw.rect(surface, ACCENT_RED, (vbar_x, y, vfill_w, vbar_h), border_radius=3)
        pygame.draw.rect(surface, (40, 18, 30), (vbar_x, y, vbar_w, vbar_h), 1, border_radius=3)
        y += vbar_h + 18

        # ── memory fragment text ──────────────────────────────────────────────
        frag_label = self._font_sm.render("[ MEMORY FRAGMENT ]", True, TEXT_MUTED)
        surface.blit(frag_label, frag_label.get_rect(centerx=cx, y=y))
        y += frag_label.get_height() + 6

        frag_text = (
            (self._room or {}).get("memory_fragment") or
            "A fragment of memory reassembles, faint but real."
        )
        if self._revealed:
            frag_w = panel.w - 80
            lines  = self._wrap(frag_text, self._font_body, frag_w)
            box_h  = len(lines) * (self._font_body.get_height() + 4) + 22
            box    = pygame.Rect(cx - frag_w // 2 - 10, y, frag_w + 20, box_h)
            pygame.draw.rect(surface, BG_PANEL, box, border_radius=6)
            pygame.draw.rect(surface, ACCENT_CYAN, box, 1, border_radius=6)
            ty = y + 11
            for line in lines:
                ls = self._font_body.render(line, True, TEXT_PRIMARY)
                surface.blit(ls, ls.get_rect(centerx=cx, y=ty))
                ty += self._font_body.get_height() + 4
            y += box_h + 14

            # ── notification banner (newly unlocked room or virus defeated) ───
            if self._is_final:
                self._draw_banner_final(surface, cx, y, panel)
            elif self._newly_unlocked:
                self._draw_banner_unlock(surface, cx, y, panel, self._newly_unlocked)
        else:
            ph = self._font_body.render(
                "Recovering fragment" + "." * (int(self._time * 3) % 4),
                True, TEXT_MUTED,
            )
            surface.blit(ph, ph.get_rect(centerx=cx, y=y))

    def _draw_banner_final(self, surface: pygame.Surface,
                            cx: int, y: int, panel: pygame.Rect) -> None:
        bw  = panel.w - 60
        box = pygame.Rect(cx - bw // 2, y, bw, 50)
        pygame.draw.rect(surface, (28, 22, 0), box, border_radius=5)
        pulse_col = ACCENT_GOLD
        pygame.draw.rect(surface, pulse_col, box, 1, border_radius=5)
        pygame.draw.rect(surface, pulse_col,
                         pygame.Rect(box.x + 4, y + 8, 3, 34), border_radius=2)
        title = self._font_sm.render("✓  VIRUS DEFEATED — ALL MEMORY RESTORED", True, ACCENT_GOLD)
        surface.blit(title, (box.x + 14, y + 8))
        sub = self._font_sm.render(
            "Return to the World Map to view the Ending Sequence.", True, TEXT_DIM
        )
        surface.blit(sub, (box.x + 14, y + 8 + title.get_height() + 4))

    def _draw_banner_unlock(self, surface: pygame.Surface,
                             cx: int, y: int, panel: pygame.Rect, room: dict) -> None:
        bw  = panel.w - 60
        box = pygame.Rect(cx - bw // 2, y, bw, 50)
        pygame.draw.rect(surface, (0, 24, 10), box, border_radius=5)
        pygame.draw.rect(surface, ACCENT_GREEN, box, 1, border_radius=5)
        pygame.draw.rect(surface, ACCENT_GREEN,
                         pygame.Rect(box.x + 4, y + 8, 3, 34), border_radius=2)
        title = self._font_sm.render(
            f"▶  NEW ROOM UNLOCKED:  {room['title']}", True, ACCENT_GREEN
        )
        surface.blit(title, (box.x + 14, y + 8))
        detail = self._font_sm.render(
            f"Tier {room['tier']}  ·  {room.get('concept', '')}", True, TEXT_DIM
        )
        surface.blit(detail, (box.x + 14, y + 8 + title.get_height() + 4))

    # ── three action buttons ──────────────────────────────────────────────────

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        for btn in self._btns:
            self._draw_one_btn(surface, btn)

    def _draw_one_btn(self, surface: pygame.Surface, btn: dict) -> None:
        r    = btn["rect"]
        hov  = btn["hover"]
        col  = btn["col"]
        is_primary = btn["key"] == "continue"

        if hov:
            fill = self._hover_fill(col)
            bc   = col
            tc   = col
        elif is_primary:
            pulse = 0.60 + 0.40 * abs(math.sin(self._time * 2.0))
            r0, g0, b0 = BORDER
            ra, ga, ba = ACCENT_GREEN
            bc   = (int(r0+(ra-r0)*pulse), int(g0+(ga-g0)*pulse), int(b0+(ba-b0)*pulse))
            fill = BG_PANEL
            tc   = TEXT_PRIMARY
        else:
            bc   = BORDER
            fill = BG_PANEL
            tc   = TEXT_DIM

        pygame.draw.rect(surface, fill, r, border_radius=4)
        pygame.draw.rect(surface, bc,   r, 2, border_radius=4)
        lbl = self._font_btn.render(btn["label"], True, tc)
        surface.blit(lbl, lbl.get_rect(center=r.center))

    @staticmethod
    def _hover_fill(col: tuple) -> tuple:
        if col == ACCENT_GREEN: return (0, 55, 28)
        if col == ACCENT_CYAN:  return (0, 30, 52)
        return (28, 28, 40)

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
