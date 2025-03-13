from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.canvas import Canvas
from kivy.uix.widget import Widget
from kivy.core.window import Window
from snake import Snake
from food import Food

class Game(Widget):
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_over = False
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.canvas_rect = None
        self._update_rect()

        Clock.schedule_interval(self.update, 1.0 / 10.0)
        Window.bind(on_key_down=self.on_key_down)

    def _update_rect(self, *args):
        if self.canvas_rect:
            self.canvas.remove(self.canvas_rect)
        with self.canvas:
            Color(0, 0, 0, 1)
            self.canvas_rect = Rectangle(size=self.size, pos=self.pos)

    def update(self, dt):
        if not self.game_over:
            self.snake.move()
            if self.snake.check_collision(self.food):
                self.snake.grow()
                self.food.spawn_food()
                self.score += 1
            self.check_game_over()

    def check_game_over(self):
        if self.snake.check_collision_with_boundaries(self.width, self.height):
            self.game_over = True

    def on_key_down(self, window, key, *args):
        if key == 273:  # Up arrow
            self.snake.change_direction(0, 1)
        elif key == 274:  # Down arrow
            self.snake.change_direction(0, -1)
        elif key == 275:  # Right arrow
            self.snake.change_direction(1, 0)
        elif key == 276:  # Left arrow
            self.snake.change_direction(-1, 0)

class SnakeGameApp(App):
    def build(self):
        return Game()

if __name__ == '__main__':
    SnakeGameApp().run()