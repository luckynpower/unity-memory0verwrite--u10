import pygame
from abc import ABC, abstractmethod


class BaseScene(ABC):
    def __init__(self, game):
        self.game = game

    def on_enter(self, **kwargs) -> None:
        """Called once when the state machine transitions into this scene."""

    def on_exit(self) -> None:
        """Called once when the state machine transitions away from this scene."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self, dt: float) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
