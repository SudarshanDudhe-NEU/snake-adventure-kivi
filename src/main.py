from .game import SnakeGame
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config

# Set window size and prevent resizing
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')


class SnakeApp(App):
    def build(self):
        # Set window properties
        Window.title = "Snake Adventure"

        # Create and return the game widget
        game = SnakeGame()

        # Start game clock at 10 FPS
        Clock.schedule_interval(game.update, 1.0/10.0)

        return game


def main():
    SnakeApp().run()


if __name__ == '__main__':
    main()
