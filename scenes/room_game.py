import importlib
import pygame
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, BG_DARK, BG_MID, TEXT_DIM, TEXT_MUTED,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_RED,
    BORDER, ROOM_MODULE_MAP,
)

_TIMER_CX = SCREEN_WIDTH // 2   # centred in the header


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
        self._room          = None
        self._room_id       = ""
        self._font          = pygame.font.SysFont("consolas", 20)
        self._font_sm       = pygame.font.SysFont("consolas", 14)
        self._font_timer    = pygame.font.SysFont("consolas", 22, bold=True)
        self._timer_remaining = 0.0
        self._time            = 0.0

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self, room_id: str = "", timer_seconds: int = 600, **kwargs) -> None:
        self._room_id         = room_id
        self._room            = _load_room(room_id, self.game)
        self._timer_remaining = float(timer_seconds)
        self._time            = 0.0
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
        self._time += dt
        if self._timer_remaining > 0:
            self._timer_remaining -= dt
        if self._room:
            self._room.update(dt)
            if self._room.is_complete:
                score          = self._room.get_score()
                max_score      = getattr(self._room, "MAX_SCORE", 500)
                is_first_clear = not self.game.save.is_cleared(self._room_id)
                self.game.save.mark_cleared(self._room_id, score)
                self.game.sm.transition(
                    "room_result",
                    room_id=self._room_id,
                    score=score,
                    max_score=max_score,
                    is_first_clear=is_first_clear,
                )

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        if self._room:
            self._room.draw(surface)
        else:
            self._draw_placeholder(surface)
        self._draw_timer(surface)

    def _draw_timer(self, surface: pygame.Surface) -> None:
        remaining = max(0.0, self._timer_remaining)
        minutes   = int(remaining // 60)
        seconds   = int(remaining % 60)
        time_str  = f"{minutes:02d}:{seconds:02d}"

        expired = remaining <= 0
        if expired:
            # Blink at 2 Hz when expired
            if int(self._time * 2) % 2 == 0:
                return
            col = ACCENT_RED
        elif remaining <= 60:
            col = ACCENT_RED
        elif remaining <= 180:
            col = ACCENT_ORANGE
        else:
            col = ACCENT_CYAN

        txt = self._font_timer.render(time_str, True, col)
        pad = 12
        box = pygame.Rect(
            _TIMER_CX - txt.get_width() // 2 - pad,
            12,
            txt.get_width() + pad * 2,
            txt.get_height() + 8,
        )
        pygame.draw.rect(surface, BG_MID, box, border_radius=4)
        pygame.draw.rect(surface, col,    box, 1, border_radius=4)
        surface.blit(txt, (box.x + pad, box.y + 4))

        if expired:
            warn = self._font_sm.render("TIME EXPIRED", True, ACCENT_RED)
            surface.blit(warn, warn.get_rect(centerx=_TIMER_CX, y=box.bottom + 2))

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
