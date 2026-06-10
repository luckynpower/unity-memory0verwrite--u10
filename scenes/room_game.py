import importlib
import pygame
from scenes.base_scene import BaseScene
from core.settings import BG_DARK, BG_MID, TEXT_DIM, TEXT_MUTED, ACCENT_CYAN, BORDER, ROOM_MODULE_MAP


def _load_room(room_id: str, game):
    module_path = ROOM_MODULE_MAP.get(room_id)
    if module_path is None:
        return None
    try:
        module = importlib.import_module(module_path)
        return module.Room(game)
    except (ModuleNotFoundError, AttributeError):
        return None


class RoomGame(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._room     = None
        self._room_id  = ""
        self._font     = pygame.font.SysFont("consolas", 20)
        self._font_sm  = pygame.font.SysFont("consolas", 14)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self, room_id: str = "", **kwargs) -> None:
        self._room_id = room_id
        self._room    = _load_room(room_id, self.game)
        if self._room:
            self._room.setup()

    def on_exit(self) -> None:
        if self._room:
            self._room.teardown()
            self._room = None

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.audio.play("click")
            self.game.sm.transition("rooms")
            return
        if self._room:
            self._room.handle_event(event)

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        if self._room:
            self._room.update(dt)
            if self._room.is_complete:
                score     = self._room.get_score()
                max_score = getattr(self._room, "MAX_SCORE", 500)
                self.game.save.mark_cleared(self._room_id, score)
                self.game.sm.transition(
                    "room_result",
                    room_id=self._room_id,
                    score=score,
                    max_score=max_score,
                )

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        if self._room:
            self._room.draw(surface)
        else:
            self._draw_placeholder(surface)

    def _draw_placeholder(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        cx, cy = surface.get_width() // 2, surface.get_height() // 2
        box = pygame.Rect(cx - 320, cy - 70, 640, 140)
        pygame.draw.rect(surface, BG_MID, box, border_radius=6)
        pygame.draw.rect(surface, BORDER, box, 2, border_radius=6)
        msg = self._font.render(
            f"Room '{self._room_id}' is not yet implemented.", True, TEXT_DIM
        )
        surface.blit(msg, msg.get_rect(center=(cx, cy - 14)))
        hint = self._font_sm.render(
            "Press ESC to return to the rooms screen.", True, TEXT_MUTED
        )
        surface.blit(hint, hint.get_rect(center=(cx, cy + 18)))
