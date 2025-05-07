import pygame
import sys
from snake import Snake
from food import Food
from obstacle import Obstacle  # If you've added the obstacle class
# Added DARK_GREY here
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, DARK_GREY


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.snake = Snake()
        self.food = Food()
        self.obstacles = Obstacle(count=7)  # Create obstacles
        self.font = pygame.font.SysFont('arial', 25)
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.paused = False  # Add paused state

        # Make sure food doesn't spawn on an obstacle or snake
        self.reposition_food()

    def reposition_food(self):
        """Make sure food doesn't spawn on obstacles or the snake"""
        while (self.food.position in self.obstacles.positions or
               self.food.position in self.snake.positions):
            self.food.randomize_position()

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:  # 'P' key for pause/play
                    self.paused = not self.paused
                elif not self.game_over and not self.paused and event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.snake.turn(event.key)
                elif self.game_over and event.key == pygame.K_RETURN:
                    self.reset()

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.obstacles = Obstacle(count=7)  # New obstacles on reset
        self.reposition_food()
        self.game_over = False
        self.paused = False  # Unpause when resetting

    def update(self):
        if self.game_over or self.paused:  # Don't update if paused
            return

        # Move the snake and check for collision with itself
        self.game_over = self.snake.move()

        # Check if snake has hit an obstacle (if obstacles are implemented)
        if hasattr(self, 'obstacles') and self.snake.get_head_position() in self.obstacles.positions:
            self.game_over = True
            return

        # Check if snake has eaten the food
        if self.snake.get_head_position() == self.food.position:
            # Change the snake's color to the food's color
            self.snake.change_color(self.food.color)

            # Grow the snake
            self.snake.grow()

            # Generate new food with a new color
            self.food.new_food()

            # Make sure food doesn't spawn on obstacles or snake
            if hasattr(self, 'obstacles'):
                while (self.food.position in self.obstacles.positions or
                       self.food.position in self.snake.positions):
                    self.food.randomize_position()
            else:
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()

    def draw(self):
        self.surface.fill(DARK_GREY)  # Changed from BLACK to DARK_GREY

        # Draw obstacles first so they appear behind the snake and food
        self.obstacles.draw(self.surface)
        self.snake.draw(self.surface)
        self.food.draw(self.surface)

        score_text = self.font.render(
            f"Score: {self.snake.score}", True, WHITE)
        self.surface.blit(score_text, (10, 10))

        # Display pause status
        if self.paused:
            pause_text = self.font.render(
                "PAUSED - Press P to continue", True, WHITE)
            text_rect = pause_text.get_rect(
                center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
            self.surface.blit(pause_text, text_rect)

            # Draw a simple pause icon
            pause_icon_left = pygame.Rect(
                WINDOW_WIDTH//2 - 20, WINDOW_HEIGHT//2, 10, 30)
            pause_icon_right = pygame.Rect(
                WINDOW_WIDTH//2 + 10, WINDOW_HEIGHT//2, 10, 30)
            pygame.draw.rect(self.surface, WHITE, pause_icon_left)
            pygame.draw.rect(self.surface, WHITE, pause_icon_right)

        # Controls info
        controls_text = self.font.render("P: Pause/Play", True, WHITE)
        self.surface.blit(controls_text, (WINDOW_WIDTH - 150, 10))

        if self.game_over:
            game_over_text = self.font.render(
                "GAME OVER! Press Enter to restart", True, WHITE)
            text_rect = game_over_text.get_rect(
                center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.surface.blit(game_over_text, text_rect)

        pygame.display.update()
