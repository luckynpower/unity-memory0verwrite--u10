"""
Two-page intro scene.
  Page 0 — Story setup with typewriter effect.
  Page 1 — How-to-play briefing (static).
SPACE / ENTER skips the typewriter on page 0.
"""
import math
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED,
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

_HOW_TO_PLAY: list[str] = [
    "HOW IT WORKS",
    "",
    "  Enter a room and solve its cybersecurity puzzle.",
    "  Each puzzle teaches a real technique used by professionals.",
    "",
    "  Complete a room  ->  recover a memory fragment.",
    "  Recover all 8 fragments  ->  defeat the virus.",
    "",
    "  Rooms increase in difficulty: Tier 1 through Tier 4.",
    "  Two rooms are available now. More are coming.",
    "",
    "  Your progress is saved automatically between sessions.",
    "  You can replay any completed room to improve your score.",
    "",
    "  Press M at any time to toggle sound.",
    "  Press ESC inside a room to return to the room selection screen.",
]

_CHARS_PER_SEC = 45.0
_HEADING_COL   = ACCENT_CYAN
_ALERT_COL     = ACCENT_RED


class Intro(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_head = pygame.font.SysFont("consolas", 20, bold=True)
        self._font_body = pygame.font.SysFont("consolas", 17)
        self._font_sm   = pygame.font.SysFont("consolas", 13)
        self._font_btn  = pygame.font.SysFont("consolas", 20, bold=True)

    def on_enter(self, **kwargs) -> None:
        self._page        = 0
        self._char_index  = 0.0   # fractional char counter for typewriter
        self._full_text   = "\n".join(_STORY)
        self._skip        = False  # once True, show full text immediately
        self._btn_hover   = False
        self._time        = 0.0
        self.game.audio.start_ambient()

    def on_exit(self) -> None:
        pass

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._advance()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._get_btn_rect().collidepoint(event.pos):
                self.game.audio.play("click")
                self._advance()

    def _advance(self) -> None:
        if self._page == 0:
            if not self._skip:
                # First press: skip typewriter
                self._skip = True
            else:
                # Second press / button click: go to page 1
                self._page = 1
        else:
            self.game.audio.play("click")
            self.game.sm.transition("rooms")

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        if self._page == 0 and not self._skip:
            self._char_index = min(
                len(self._full_text),
                self._char_index + _CHARS_PER_SEC * dt,
            )
            # Auto-complete: show CONTINUE button as soon as typewriter finishes
            if self._char_index >= len(self._full_text):
                self._skip = True
        mx, my = pygame.mouse.get_pos()
        self._btn_hover = self._get_btn_rect().collidepoint(mx, my)

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        if self._page == 0:
            self._draw_story(surface)
        else:
            self._draw_howto(surface)
        self._draw_button(surface)
        fx.scanlines(surface, alpha=22)

    def _draw_story(self, surface: pygame.Surface) -> None:
        visible = self._full_text if self._skip else self._full_text[:int(self._char_index)]
        lines   = visible.split("\n")

        x  = SCREEN_WIDTH // 2 - 340
        y  = 80
        lh = self._font_body.get_height() + 6

        for line in lines:
            if line.startswith("SYSTEM ALERT"):
                surf = self._font_head.render(line, True, _ALERT_COL)
            elif line == "":
                y += lh // 2
                continue
            else:
                surf = self._font_body.render(line, True, TEXT_PRIMARY)
            surface.blit(surf, (x, y))
            y += lh

        # Blinking cursor while typing
        if not self._skip and int(self._char_index) < len(self._full_text):
            if int(self._time * 2) % 2 == 0:
                csr = self._font_body.render("_", True, ACCENT_GREEN)
                surface.blit(csr, (x + self._font_body.size(lines[-1])[0] + 2, y - lh))

        if self._skip:
            skip_hint = self._font_sm.render(
                "Press SPACE or click CONTINUE to proceed.", True, TEXT_MUTED
            )
            surface.blit(skip_hint, skip_hint.get_rect(centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 110))

    def _draw_howto(self, surface: pygame.Surface) -> None:
        x  = SCREEN_WIDTH // 2 - 340
        y  = 60
        lh = self._font_body.get_height() + 6

        for line in _HOW_TO_PLAY:
            if line == "HOW IT WORKS":
                surf = self._font_head.render(line, True, ACCENT_CYAN)
                surface.blit(surf, (x, y))
                y += surf.get_height() + 4
                # underline
                pygame.draw.line(surface, BORDER, (x, y), (x + 480, y), 1)
                y += 10
            elif line == "":
                y += lh // 2
            elif line.startswith("  ") and "->" in line:
                parts = line.split("->")
                s1 = self._font_body.render(parts[0], True, TEXT_DIM)
                surface.blit(s1, (x, y))
                s2 = self._font_body.render("->", True, ACCENT_GREEN)
                surface.blit(s2, (x + s1.get_width(), y))
                s3 = self._font_body.render(parts[1], True, TEXT_PRIMARY)
                surface.blit(s3, (x + s1.get_width() + s2.get_width(), y))
                y += lh
            else:
                col = TEXT_DIM if line.startswith("  ") else TEXT_PRIMARY
                surf = self._font_body.render(line, True, col)
                surface.blit(surf, (x, y))
                y += lh

    def _draw_button(self, surface: pygame.Surface) -> None:
        r = self._get_btn_rect()

        if self._page == 1:
            # "ENTER THE SYSTEM" — green, pulsing
            active_col = ACCENT_GREEN
            label      = "ENTER THE SYSTEM  >"
        elif self._skip:
            # Typewriter done — prominent CONTINUE button
            active_col = ACCENT_CYAN
            label      = "CONTINUE  >"
        else:
            # Typewriter still running — dim SKIP hint
            pygame.draw.rect(surface, BG_PANEL, r, border_radius=4)
            pygame.draw.rect(surface, BORDER,   r, 1, border_radius=4)
            txt = self._font_btn.render("SKIP INTRO", True, TEXT_MUTED)
            surface.blit(txt, txt.get_rect(center=r.center))
            return

        pulse      = 0.65 + 0.35 * abs(math.sin(self._time * 2.5))
        r0, g0, b0 = BORDER
        ra, ga, ba = active_col
        border_col = (
            active_col if self._btn_hover else
            (int(r0 + (ra - r0) * pulse),
             int(g0 + (ga - g0) * pulse),
             int(b0 + (ba - b0) * pulse))
        )
        fill = (
            (0, 52, 30) if (self._btn_hover and active_col == ACCENT_GREEN) else
            (0, 30, 52) if (self._btn_hover and active_col == ACCENT_CYAN) else
            BG_PANEL
        )
        text_col = active_col if self._btn_hover else TEXT_PRIMARY

        pygame.draw.rect(surface, fill,       r, border_radius=4)
        pygame.draw.rect(surface, border_col, r, 2, border_radius=4)
        txt = self._font_btn.render(label, True, text_col)
        surface.blit(txt, txt.get_rect(center=r.center))

    def _get_btn_rect(self) -> pygame.Rect:
        w = 280 if self._page == 0 else 340
        return pygame.Rect(
            SCREEN_WIDTH // 2 - w // 2,
            SCREEN_HEIGHT - 80,
            w, 44,
        )
