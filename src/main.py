from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from game import Game

class SnakeGameApp(App):
    def build(self):
        self.game = Game()
        return self.game

    def update(self, dt):
        self.game.update()

if __name__ == '__main__':
    SnakeGameApp().run()