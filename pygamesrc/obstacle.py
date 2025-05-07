import pygame
import random
from constants import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT


class Obstacle:
    def __init__(self, count=5):
        self.positions = []
        self.color = (139, 69, 19)  # Brown color for obstacles
        self.generate_obstacles(count)

    def generate_obstacles(self, count):
        """Generate random obstacles on the grid"""
        self.positions = []
        for _ in range(count):
            # Generate a random position
            pos = (random.randint(2, GRID_WIDTH - 3),
                   random.randint(2, GRID_HEIGHT - 3))
            # Make sure obstacles don't overlap
            while pos in self.positions:
                pos = (random.randint(2, GRID_WIDTH - 3),
                       random.randint(2, GRID_HEIGHT - 3))
            self.positions.append(pos)

    def draw(self, surface):
        """Draw all obstacles on the surface"""
        for position in self.positions:
            rect = pygame.Rect(
                position[0] * GRID_SIZE,
                position[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, (100, 50, 0), rect, 1)  # Darker outline
