"""
Story intro — shown on fresh game start.
Single animated page: typewriter story → fragment/virus visualization → Begin Recovery.
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

_STORY: list[str] = [
    "SYSTEM ALERT  //  MEMORY CORRUPTION DETECTED",
    "",
    "A memory-stealing virus has infiltrated the network.",
    "Your identity — your name, your skills, your past —",
    "has been encrypted and scattered across eight corrupted rooms.",
    "",
    "Each room contains a stolen memory fragment.",
    "Solve its puzzle. Recover the fragment.",
    "Weaken the virus.",
    "",
    "You are a cyber guard.",
    "This is your domain.",
    "Take it back.",
]

_CHARS_PER_SEC = 45.0
_SLOT_DELAY    = 0.12   # seconds between successive fragment slot reveals
_BTN_SHOW_T    = 1.4    # seconds after text is complete before button appears

_SLOT_W   = 60
_SLOT_H   = 52
_SLOT_GAP = 12
_SLOT_TOTAL_W = len(ROOMS) * _SLOT_W + (len(ROOMS) - 1) * _SLOT_GAP
_SLOT_X0  = (SCREEN_WIDTH - _SLOT_TOTAL_W) // 2


class Intro(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_logo  = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_head  = pygame.font.SysFont("consolas", 20, bold=True)
        self._font_body  = pygame.font.SysFont("consolas", 17)
        self._font_sm    = pygame.font.SysFont("consolas", 13)
        self._font_btn   = pygame.font.SysFont("consolas", 20, bold=True)
        self._font_slot  = pygame.font.SysFont("consolas", 13, bold=True)

    def on_enter(self, **kwargs) -> None:
        self._char_index = 0.0
        self._full_text  = "\n".join(_STORY)
        self._skip       = False
        self._phase2_t   = 0.0
        self._btn_hover  = False
        self._time       = 0.0
        self.game.audio.start_ambient()

    def on_exit(self) -> None:
        pass

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._advance()
            elif event.key == pygame.K_ESCAPE:
                self.game.audio.play("click")
                self.game.sm.transition("main_menu")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._skip and self._phase2_t >= _BTN_SHOW_T:
                if self._get_btn_rect().collidepoint(event.pos):
                    self.game.audio.play("click")
                    self.game.sm.transition("rooms")

    def _advance(self) -> None:
        if not self._skip:
            self._skip     = True
            self._phase2_t = 0.0
        elif self._phase2_t < _BTN_SHOW_T:
            self._phase2_t = 2.0   # skip reveal animation
        else:
            self.game.audio.play("click")
            self.game.sm.transition("rooms")

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        if not self._skip:
            self._char_index = min(
                len(self._full_text),
                self._char_index + _CHARS_PER_SEC * dt,
            )
            if self._char_index >= len(self._full_text):
                self._skip     = True
                self._phase2_t = 0.0
        else:
            self._phase2_t = min(2.0, self._phase2_t + dt)

        mx, my = pygame.mouse.get_pos()
        self._btn_hover = self._get_btn_rect().collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_bg_noise(surface)
        self._draw_logo(surface)
        self._draw_story(surface)
        if self._skip:
            self._draw_fragments(surface)
            self._draw_virus_bar(surface)
        if self._skip and self._phase2_t >= _BTN_SHOW_T:
            self._draw_button(surface)
        self._draw_skip_hint(surface)
        fx.scanlines(surface, alpha=22)

    def _draw_bg_noise(self, surface: pygame.Surface) -> None:
        rng = random.Random(int(self._time * 18))
        for _ in range(60):
            x = rng.randint(0, SCREEN_WIDTH  - 1)
            y = rng.randint(0, SCREEN_HEIGHT - 1)
            v = rng.randint(18, 55)
            surface.set_at((x, y), (v, v + 18, v + 36))

    def _draw_logo(self, surface: pygame.Surface) -> None:
        logo = self._font_logo.render("MEMORY0VERWRITE", True, ACCENT_CYAN)
        surface.blit(logo, logo.get_rect(centerx=SCREEN_WIDTH // 2, y=16))
        pygame.draw.line(
            surface, BORDER,
            (SCREEN_WIDTH // 2 - 240, 50),
            (SCREEN_WIDTH // 2 + 240, 50), 1,
        )

    def _draw_story(self, surface: pygame.Surface) -> None:
        visible = self._full_text if self._skip else self._full_text[:int(self._char_index)]
        lines   = visible.split("\n")

        lh = self._font_body.get_height() + 5
        x  = SCREEN_WIDTH // 2 - 340
        y  = 66

        for line in lines:
            if line.startswith("SYSTEM ALERT"):
                surf = self._font_head.render(line, True, ACCENT_RED)
            elif line == "":
                y += lh // 2
                continue
            else:
                surf = self._font_body.render(line, True, TEXT_PRIMARY)
            surface.blit(surf, (x, y))
            y += lh

        if not self._skip and int(self._char_index) < len(self._full_text):
            if int(self._time * 2) % 2 == 0:
                csr = self._font_body.render("_", True, ACCENT_GREEN)
                surface.blit(csr, (x + self._font_body.size(lines[-1])[0] + 2, y - lh))

    def _draw_fragments(self, surface: pygame.Surface) -> None:
        y_slot  = 349
        y_label = y_slot + _SLOT_H + 6

        total   = len(ROOMS)
        cleared = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))

        for i, room in enumerate(ROOMS):
            reveal_t = i * _SLOT_DELAY
            if self._phase2_t < reveal_t:
                continue

            x_slot = _SLOT_X0 + i * (_SLOT_W + _SLOT_GAP)
            slot_r = pygame.Rect(x_slot, y_slot, _SLOT_W, _SLOT_H)

            is_cleared = self.game.save.is_cleared(room["id"])
            if is_cleared:
                fill_col   = (28, 22, 0)
                border_col = ACCENT_GOLD
                txt_col    = ACCENT_GOLD
                txt        = f"{room['number']:02d}"
            else:
                fill_col   = BG_PANEL
                border_col = (55, 40, 80)
                txt_col    = TEXT_MUTED
                txt        = "??"

            pygame.draw.rect(surface, fill_col,   slot_r, border_radius=4)
            pygame.draw.rect(surface, border_col, slot_r, 1, border_radius=4)
            t = self._font_slot.render(txt, True, txt_col)
            surface.blit(t, t.get_rect(center=slot_r.center))

        lbl = self._font_sm.render(
            f"MEMORY FRAGMENTS:  {cleared} / {total}", True,
            ACCENT_GOLD if cleared > 0 else TEXT_DIM,
        )
        surface.blit(lbl, lbl.get_rect(centerx=SCREEN_WIDTH // 2, y=y_label))

    def _draw_virus_bar(self, surface: pygame.Surface) -> None:
        cx     = SCREEN_WIDTH // 2
        total  = len(ROOMS)
        cleared = sum(1 for r in ROOMS if self.game.save.is_cleared(r["id"]))
        virus_pct = 1.0 - (cleared / total)

        bar_w  = 640
        bar_h  = 20
        bar_x  = cx - bar_w // 2
        bar_y  = 450

        # animated fill
        fill_ratio = min(virus_pct, self._phase2_t * virus_pct) if self._phase2_t < 1.0 else virus_pct

        # label above bar
        status   = "ACTIVE" if virus_pct > 0 else "CONTAINED"
        s_col    = ACCENT_RED if virus_pct > 0 else ACCENT_GREEN
        lbl_surf = self._font_sm.render(
            f"VIRUS STRENGTH:  {int(virus_pct * 100)}%  [{status}]", True, s_col
        )
        surface.blit(lbl_surf, lbl_surf.get_rect(centerx=cx, y=bar_y - 20))

        pygame.draw.rect(surface, BG_PANEL, (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * fill_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, ACCENT_RED, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, (80, 18, 40), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=5)

        hint = self._font_sm.render(
            "Recover all fragments to defeat the virus.", True, TEXT_MUTED
        )
        surface.blit(hint, hint.get_rect(centerx=cx, y=bar_y + bar_h + 6))

    def _draw_button(self, surface: pygame.Surface) -> None:
        r = self._get_btn_rect()
        pulse      = 0.65 + 0.35 * abs(math.sin(self._time * 2.5))
        r0, g0, b0 = BORDER
        ra, ga, ba = ACCENT_GREEN
        border_col = (
            ACCENT_GREEN if self._btn_hover else
            (int(r0 + (ra - r0) * pulse),
             int(g0 + (ga - g0) * pulse),
             int(b0 + (ba - b0) * pulse))
        )
        fill     = (0, 52, 30) if self._btn_hover else BG_PANEL
        text_col = ACCENT_GREEN if self._btn_hover else TEXT_PRIMARY
        pygame.draw.rect(surface, fill,       r, border_radius=5)
        pygame.draw.rect(surface, border_col, r, 2, border_radius=5)
        lbl = self._font_btn.render("BEGIN RECOVERY  >", True, text_col)
        surface.blit(lbl, lbl.get_rect(center=r.center))

    def _draw_skip_hint(self, surface: pygame.Surface) -> None:
        if not self._skip:
            hint = "SPACE to skip  |  ESC to return to menu"
        elif self._phase2_t < _BTN_SHOW_T:
            hint = "SPACE to skip animation"
        else:
            hint = "ENTER to begin recovery"
        s = self._font_sm.render(hint, True, TEXT_MUTED)
        surface.blit(s, s.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 28))

    def _get_btn_rect(self) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - 190, 510, 380, 52)
