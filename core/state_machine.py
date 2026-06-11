import logging
import pygame

log = logging.getLogger("sm")


class StateMachine:
    def __init__(self):
        self._states: dict = {}
        self._current = None
        self._current_name: str = ""

    def register(self, name: str, state) -> None:
        self._states[name] = state

    def transition(self, name: str, **kwargs) -> None:
        prev = self._current_name or "(none)"
        log.info("transition  %s  ->  %s  kwargs=%s", prev, name, list(kwargs.keys()))
        if self._current is not None:
            self._current.on_exit()
        self._current_name = name
        self._current = self._states[name]
        self._current.on_enter(**kwargs)
        log.debug("transition complete -> %s", name)

    @property
    def current_name(self) -> str:
        return self._current_name

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._current:
            self._current.handle_event(event)

    def update(self, dt: float) -> None:
        if self._current:
            self._current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self._current:
            self._current.draw(surface)
