from game import Game
from constants import FRAMERATE


def main():
    game = Game()

    # Game loop
    while True:
        game.handle_keys()
        game.update()
        game.draw()
        game.clock.tick(FRAMERATE)


if __name__ == "__main__":
    main()
