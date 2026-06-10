import math
import pygame
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_PANEL, BG_MID,
    ACCENT_GREEN, ACCENT_CYAN,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)


class MainMenu(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_title = pygame.font.SysFont("consolas", 62, bold=True)
        self._font_sub   = pygame.font.SysFont("consolas", 18)
        self._font_btn   = pygame.font.SysFont("consolas", 24, bold=True)
        self._font_hint  = pygame.font.SysFont("consolas", 13)
        self._buttons: list[dict] = []
        self._time = 0.0

    def on_enter(self, **kwargs) -> None:
        cx = SCREEN_WIDTH // 2
        self._buttons = [
            {"label": "PLAY",  "rect": pygame.Rect(cx - 130, 370, 260, 54), "action": "play"},
            {"label": "QUIT",  "rect": pygame.Rect(cx - 130, 440, 260, 54), "action": "quit"},
        ]

    # ---------------------------------------------------------------- events

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self._buttons:
                if btn["rect"].collidepoint(event.pos):
                    if btn["action"] == "play":
                        self.game.sm.transition("world_map")
                    else:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ---------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        self._time += dt

    # ---------------------------------------------------------------- draw

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_grid(surface)
        self._draw_title(surface)
        self._draw_buttons(surface)
        self._draw_footer(surface)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        """Faint dot-grid background."""
        spacing = 40
        alpha_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(0, SCREEN_WIDTH, spacing):
            for y in range(0, SCREEN_HEIGHT, spacing):
                pygame.draw.circle(alpha_surf, (40, 55, 90, 120), (x, y), 1)
        surface.blit(alpha_surf, (0, 0))

    def _draw_title(self, surface: pygame.Surface) -> None:
        pulse = abs(math.sin(self._time * 1.4))
        r = int(0   + pulse * 0)
        g = int(180 + pulse * 40)
        b = int(100 + pulse * 155)
        title = self._font_title.render("CYBER ESCAPE", True, (r, g, b))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))

        tag = self._font_sub.render(
            "Your memories have been stolen. Take them back.", True, TEXT_DIM
        )
        surface.blit(tag, tag.get_rect(center=(SCREEN_WIDTH // 2, 262)))

        ver = self._font_hint.render("v0.1  MVP", True, TEXT_MUTED)
        surface.blit(ver, ver.get_rect(center=(SCREEN_WIDTH // 2, 290)))

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        mx, my = pygame.mouse.get_pos()
        for btn in self._buttons:
            hovered = btn["rect"].collidepoint(mx, my)
            fill   = (0, 55, 30) if hovered else BG_PANEL
            border = ACCENT_GREEN if hovered else BORDER
            text   = ACCENT_GREEN if hovered else TEXT_DIM
            pygame.draw.rect(surface, fill,   btn["rect"], border_radius=4)
            pygame.draw.rect(surface, border, btn["rect"], 2, border_radius=4)
            label = self._font_btn.render(btn["label"], True, text)
            surface.blit(label, label.get_rect(center=btn["rect"].center))

    def _draw_footer(self, surface: pygame.Surface) -> None:
        hint = self._font_hint.render(
            "8 rooms  |  cybersecurity concepts through hands-on puzzles", True, TEXT_MUTED
        )
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))
