"""
Main menu — Memory0verwrite.
Features: matrix-rain background, glitch-title animation,
          story teaser, START MISSION / CONTINUE buttons, sound.
"""
import math
import random
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_RAIN_CHARS   = "abcdef0123456789!@#$%^&*<>?/\\{}[]ABCDEF01"
_RAIN_CHAR_W  = 14
_RAIN_CHAR_H  = 18
_RAIN_COLS    = SCREEN_WIDTH  // _RAIN_CHAR_W + 1
_RAIN_ROWS    = SCREEN_HEIGHT // _RAIN_CHAR_H + 2


class _MatrixRain:
    """Persistent-surface matrix rain renderer."""

    def __init__(self):
        self._surf    = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._surf.fill(BG_DARK)
        self._font    = pygame.font.SysFont("consolas", _RAIN_CHAR_H, bold=False)
        self._fade    = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._fade.fill((8, 10, 18, 38))   # BG_DARK with alpha — creates trail

        # Each column: current drop row position
        self._drops   = [random.randint(-_RAIN_ROWS, 0) for _ in range(_RAIN_COLS)]
        self._speeds  = [random.uniform(0.3, 1.0) for _ in range(_RAIN_COLS)]
        self._accum   = [0.0] * _RAIN_COLS

    def update(self, dt: float) -> None:
        for c in range(_RAIN_COLS):
            self._accum[c] += dt * self._speeds[c] * 18
            if self._accum[c] >= 1.0:
                self._accum[c] -= 1.0
                self._drops[c] += 1
                if self._drops[c] > _RAIN_ROWS + 5 and random.random() > 0.92:
                    self._drops[c] = random.randint(-_RAIN_ROWS, -2)
                    self._speeds[c] = random.uniform(0.3, 1.0)

    def draw(self, target: pygame.Surface) -> None:
        # Fade existing content — creates the trailing green glow
        self._surf.blit(self._fade, (0, 0))

        # Draw a new head character per column
        for c, row in enumerate(self._drops):
            x = c * _RAIN_CHAR_W
            y = row * _RAIN_CHAR_H
            if 0 <= y < SCREEN_HEIGHT:
                ch   = random.choice(_RAIN_CHARS)
                glyph = self._font.render(ch, True, (170, 255, 170))
                self._surf.blit(glyph, (x, y))

        target.blit(self._surf, (0, 0))


class MainMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_title  = pygame.font.SysFont("consolas", 68, bold=True)
        self._font_sub    = pygame.font.SysFont("consolas", 16)
        self._font_btn    = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_hint   = pygame.font.SysFont("consolas", 12)
        self._rain        = _MatrixRain()
        self._buttons: list[dict] = []
        self._time        = 0.0
        self._last_hover  = ""

    def on_enter(self, **kwargs) -> None:
        has_save = bool(self.game.save._data.get("cleared_rooms"))
        cx = SCREEN_WIDTH // 2
        self._buttons = []
        if has_save:
            self._buttons.append({
                "label": "CONTINUE MISSION",
                "rect":  pygame.Rect(cx - 190, 420, 380, 54),
                "action": "continue",
                "color": ACCENT_GREEN,
            })
            self._buttons.append({
                "label": "START OVER",
                "rect":  pygame.Rect(cx - 140, 490, 280, 44),
                "action": "new",
                "color": TEXT_DIM,
            })
        else:
            self._buttons.append({
                "label": "START MISSION",
                "rect":  pygame.Rect(cx - 170, 430, 340, 54),
                "action": "start",
                "color": ACCENT_GREEN,
            })

        self._buttons.append({
            "label": "QUIT",
            "rect":  pygame.Rect(cx - 90, 550 if has_save else 500, 180, 44),
            "action": "quit",
            "color": TEXT_MUTED,
        })
        self._time = 0.0
        self.game.audio.start_ambient()

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self._buttons:
                if btn["rect"].collidepoint(event.pos):
                    self.game.audio.play("click")
                    self._do_action(btn["action"])

    def _do_action(self, action: str) -> None:
        if action in ("start", "new"):
            if action == "new":
                # Reset save data
                self.game.save._data = {"cleared_rooms": {}, "artefacts": {}}
                self.game.save.save()
            self.game.sm.transition("intro")
        elif action == "continue":
            self.game.sm.transition("rooms")
        elif action == "quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt
        self._rain.update(dt)

        mx, my = pygame.mouse.get_pos()
        for btn in self._buttons:
            was_hovered = self._last_hover == btn["label"]
            is_hovered  = btn["rect"].collidepoint(mx, my)
            if is_hovered and not was_hovered:
                self.game.audio.play("hover")
                self._last_hover = btn["label"]
            if not is_hovered and was_hovered:
                self._last_hover = ""

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        self._rain.draw(surface)
        self._draw_vignette(surface)
        self._draw_title(surface)
        self._draw_story_teaser(surface)
        self._draw_buttons(surface)
        self._draw_footer(surface)
        fx.scanlines(surface, alpha=20)

    def _draw_vignette(self, surface: pygame.Surface) -> None:
        """Dark radial gradient from edges to keep text readable."""
        v = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(v, (8, 10, 18, 160),
                         pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        # Lighter centre
        pygame.draw.ellipse(v, (0, 0, 0, 0),
                            pygame.Rect(200, 80, 880, 560))
        surface.blit(v, (0, 0))

    def _draw_title(self, surface: pygame.Surface) -> None:
        t = self._time
        # Slow pulse on the green channel
        g = int(200 + 55 * abs(math.sin(t * 0.9)))
        b = int(80  + 40 * abs(math.sin(t * 0.7 + 1.0)))
        base_col = (0, g, b)

        # Occasional glitch: shift a copy of the title ±4px in red/cyan
        cx = SCREEN_WIDTH // 2
        if int(t * 12) % 40 == 0:   # brief glitch frame
            glitch_r = self._font_title.render("MEMORY0VERWRITE", True, (255, 40, 60))
            glitch_c = self._font_title.render("MEMORY0VERWRITE", True, (0, 220, 255))
            surface.blit(glitch_r, glitch_r.get_rect(center=(cx - 3, 175)))
            surface.blit(glitch_c, glitch_c.get_rect(center=(cx + 3, 175)))

        title = self._font_title.render("MEMORY0VERWRITE", True, base_col)
        surface.blit(title, title.get_rect(center=(cx, 175)))

        tag = self._font_sub.render(
            "A CYBERSECURITY ESCAPE GAME", True, TEXT_DIM
        )
        surface.blit(tag, tag.get_rect(center=(cx, 228)))

    def _draw_story_teaser(self, surface: pygame.Surface) -> None:
        cx  = SCREEN_WIDTH // 2
        lines = [
            "A memory-stealing virus has trapped you inside a corrupted virtual world.",
            "Eight rooms. Eight stolen memories. One chance to take them back.",
        ]
        for i, line in enumerate(lines):
            s = self._font_sub.render(line, True, TEXT_DIM)
            surface.blit(s, s.get_rect(center=(cx, 280 + i * 24)))

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        mx, my = pygame.mouse.get_pos()
        for btn in self._buttons:
            hovered  = btn["rect"].collidepoint(mx, my)
            is_main  = btn["action"] in ("start", "continue")
            border_c = btn["color"] if hovered else (BORDER if not is_main else TEXT_DIM)
            fill_c   = (0, 40, 22) if (hovered and is_main) else BG_PANEL
            text_c   = btn["color"] if hovered else (TEXT_DIM if is_main else TEXT_MUTED)

            pygame.draw.rect(surface, fill_c,   btn["rect"], border_radius=5)
            pygame.draw.rect(surface, border_c, btn["rect"], 2, border_radius=5)
            lbl = self._font_btn.render(btn["label"], True, text_c)
            surface.blit(lbl, lbl.get_rect(center=btn["rect"].center))

    def _draw_footer(self, surface: pygame.Surface) -> None:
        hints = [
            "M = toggle sound",
            "ESC = return to rooms during a mission",
        ]
        y = SCREEN_HEIGHT - 22
        x = SCREEN_WIDTH // 2
        s = self._font_hint.render("  |  ".join(hints), True, TEXT_MUTED)
        surface.blit(s, s.get_rect(center=(x, y)))
