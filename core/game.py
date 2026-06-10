import sys
import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BG_DARK
from core.state_machine import StateMachine
from core.save_manager import SaveManager


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        self.save   = SaveManager()
        self.sm     = StateMachine()
        self._register_scenes()
        self.sm.transition("main_menu")

    def _register_scenes(self) -> None:
        # Imported here to keep circular-import risk near zero.
        from scenes.main_menu import MainMenu
        from scenes.world_map import WorldMap
        from scenes.room_game import RoomGame

        self.sm.register("main_menu", MainMenu(self))
        self.sm.register("world_map",  WorldMap(self))
        self.sm.register("room_game",  RoomGame(self))

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save.save()
                    pygame.quit()
                    sys.exit()
                self.sm.handle_event(event)
            self.sm.update(dt)
            self.screen.fill(BG_DARK)
            self.sm.draw(self.screen)
            pygame.display.flip()
