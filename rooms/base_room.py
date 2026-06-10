import pygame
from abc import ABC, abstractmethod


class BaseRoom(ABC):
    """
    Base class for every puzzle room.

    Lifecycle (called by RoomGame scene):
        setup()    — called once on enter; initialise fonts, load data, build layout.
        teardown() — called once on exit; release any room-specific resources.

    Frame loop (called every frame while the room is active):
        handle_event(event)
        update(dt)
        draw(surface)

    Completion:
        is_complete  — property; return True when the room should hand control back.
        get_score()  — return the final score (0-N) to be persisted by SaveManager.
    """

    def __init__(self, game):
        self.game      = game
        self._complete = False
        self._score    = 0

    # ---------------------------------------------------------------- lifecycle

    def setup(self) -> None:
        """Override to initialise room state."""

    def teardown(self) -> None:
        """Override to release resources (sounds, large surfaces, etc.)."""

    # ---------------------------------------------------------------- frame loop

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...

    # ---------------------------------------------------------------- state

    @property
    def is_complete(self) -> bool:
        return self._complete

    def get_score(self) -> int:
        return self._score
