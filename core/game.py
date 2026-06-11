import sys
import logging
import traceback
import pygame
from core.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BG_DARK
from core.state_machine import StateMachine
from core.save_manager import SaveManager
from core.audio import AudioManager

# ── logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    filename="memory0verwrite.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
# Mirror WARNING+ to stderr so crash details appear in the console too
_ch = logging.StreamHandler(sys.stderr)
_ch.setLevel(logging.WARNING)
_ch.setFormatter(logging.Formatter("%(levelname)s  %(name)s  %(message)s"))
logging.getLogger().addHandler(_ch)

log = logging.getLogger("game")


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()
        self.save   = SaveManager()
        self.audio  = AudioManager()
        self.sm     = StateMachine()
        self._register_scenes()
        log.info("Game initialised — transitioning to main_menu")
        self.sm.transition("main_menu")

    def _register_scenes(self) -> None:
        from scenes.main_menu   import MainMenu
        from scenes.intro        import Intro
        from scenes.world_map    import WorldMap
        from scenes.context      import Context
        from scenes.room_game    import RoomGame
        from scenes.room_result  import RoomResult
        from scenes.archive      import Archive
        from scenes.ending       import Ending

        self.sm.register("main_menu",   MainMenu(self))
        self.sm.register("intro",        Intro(self))
        self.sm.register("rooms",        WorldMap(self))
        self.sm.register("context",      Context(self))
        self.sm.register("room_game",    RoomGame(self))
        self.sm.register("room_result",  RoomResult(self))
        self.sm.register("archive",      Archive(self))
        self.sm.register("ending",       Ending(self))

    def run(self) -> None:
        log.info("Game loop started")
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    log.info("pygame.QUIT received — saving and exiting")
                    self.save.save()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    self.audio.toggle_mute()
                try:
                    self.sm.handle_event(event)
                except Exception:
                    self._handle_scene_error("handle_event")

            try:
                self.sm.update(dt)
            except Exception:
                self._handle_scene_error("update")

            self.screen.fill(BG_DARK)
            try:
                self.sm.draw(self.screen)
            except Exception:
                self._handle_scene_error("draw")
                # Draw a minimal error screen so the window doesn't go blank
                font = pygame.font.SysFont("consolas", 18)
                msg  = font.render(
                    "An error occurred — returning to World Map.", True, (255, 80, 80)
                )
                self.screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2,
                                                            SCREEN_HEIGHT // 2)))

            pygame.display.flip()

    def _handle_scene_error(self, phase: str) -> None:
        scene = self.sm.current_name
        tb    = traceback.format_exc()
        log.error(
            "Unhandled exception in %s.%s — recovering to 'rooms'\n%s",
            scene, phase, tb,
        )
        # Safely recover to world map without crashing the process
        try:
            self.sm.transition("rooms")
        except Exception:
            log.critical("Recovery to 'rooms' also failed:\n%s", traceback.format_exc())
