import pygame
from rooms.base_room import BaseRoom
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_ORANGE, TEXT_DIM, TEXT_MUTED, BORDER,
)


class Room(BaseRoom):
    """Room 3 — Password Vault (placeholder)."""

    def setup(self) -> None:
        self._font_h1  = pygame.font.SysFont("consolas", 28, bold=True)
        self._font_sub = pygame.font.SysFont("consolas", 16)
        self._font_sm  = pygame.font.SysFont("consolas", 13)

        # Check for cross-room Easter egg artefact from Room 2
        self._pet_name = self.game.save.get_artefact("pet_name")

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        box = pygame.Rect(cx - 340, cy - 120, 680, 240)
        pygame.draw.rect(surface, BG_MID, box, border_radius=8)
        pygame.draw.rect(surface, ACCENT_ORANGE, box, 2, border_radius=8)

        title = self._font_h1.render("ROOM 3  //  PASSWORD VAULT", True, ACCENT_ORANGE)
        surface.blit(title, title.get_rect(center=(cx, cy - 60)))

        sub = self._font_sub.render("Coming in the next phase.", True, TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(cx, cy - 20)))

        if self._pet_name:
            egg = self._font_sub.render(
                f"Artefact detected from Room 2:  pet name = '{self._pet_name}'",
                True,
                ACCENT_ORANGE,
            )
            surface.blit(egg, egg.get_rect(center=(cx, cy + 20)))

        hint = self._font_sm.render("Press ESC to return to the world map.", True, TEXT_MUTED)
        surface.blit(hint, hint.get_rect(center=(cx, cy + 70)))
