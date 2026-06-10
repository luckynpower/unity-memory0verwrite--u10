import sys
import pygame
from core.game import Game


def main() -> None:
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
