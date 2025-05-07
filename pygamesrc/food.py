import random
import pygame
import math
from constants import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = self.generate_random_color()
        self.food_type = self.get_random_food_type()
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1),
                         random.randint(0, GRID_HEIGHT - 1))

    def generate_random_color(self):
        """Generate a bright, vibrant color"""
        # Ensure at least one component is bright (> 200)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)

        # Make sure at least one component is very bright
        brightest = random.randint(0, 2)
        if brightest == 0:
            r = random.randint(200, 255)
        elif brightest == 1:
            g = random.randint(200, 255)
        else:
            b = random.randint(200, 255)

        return (r, g, b)

    def get_random_food_type(self):
        """Choose a random food type"""
        food_types = ["mouse", "egg", "frog", "bird", "fruit", "bug"]
        return random.choice(food_types)

    def new_food(self):
        """Create new food with new color, type, and position"""
        self.color = self.generate_random_color()
        self.food_type = self.get_random_food_type()
        self.randomize_position()

    def draw_mouse(self, surface, x, y):
        """Draw a small mouse"""
        # Mouse body (oval)
        mouse_color = (150, 150, 150)  # Gray
        body_width = int(GRID_SIZE * 0.8)
        body_height = int(GRID_SIZE * 0.6)
        body_rect = pygame.Rect(
            x + (GRID_SIZE - body_width) // 2,
            y + (GRID_SIZE - body_height) // 2,
            body_width, body_height
        )
        pygame.draw.ellipse(surface, mouse_color, body_rect)

        # Mouse head (small circle at front)
        head_radius = int(GRID_SIZE * 0.2)
        head_pos = (x + GRID_SIZE - head_radius, y + GRID_SIZE // 2)
        pygame.draw.circle(surface, mouse_color, head_pos, head_radius)

        # Mouse ears (tiny circles)
        ear_radius = int(GRID_SIZE * 0.12)
        pygame.draw.circle(surface, mouse_color,
                           (head_pos[0], head_pos[1] - ear_radius * 2), ear_radius)
        pygame.draw.circle(surface, mouse_color,
                           (head_pos[0], head_pos[1] + ear_radius * 2), ear_radius)

        # Mouse tail (curved line)
        tail_start = (x + GRID_SIZE // 4, y + GRID_SIZE // 2)
        tail_mid = (x + GRID_SIZE // 8, y + GRID_SIZE * 3 // 4)
        tail_end = (x, y + GRID_SIZE // 2)
        pygame.draw.lines(surface, mouse_color, False,
                          [tail_start, tail_mid, tail_end], 2)

        # Mouse eye (tiny black dot)
        eye_radius = max(1, int(GRID_SIZE * 0.06))
        pygame.draw.circle(surface, (0, 0, 0),
                           (head_pos[0] + 1, head_pos[1] - 2), eye_radius)

    def draw_egg(self, surface, x, y):
        """Draw a small egg"""
        # Egg (oval)
        egg_color = (255, 250, 240)  # Off-white
        egg_width = int(GRID_SIZE * 0.7)
        egg_height = int(GRID_SIZE * 0.85)
        egg_rect = pygame.Rect(
            x + (GRID_SIZE - egg_width) // 2,
            y + (GRID_SIZE - egg_height) // 2,
            egg_width, egg_height
        )
        pygame.draw.ellipse(surface, egg_color, egg_rect)

        # Egg spots (tiny circles)
        spot_color = (210, 180, 140)  # Light brown
        spot_radius = max(1, int(GRID_SIZE * 0.08))
        spots = [
            (x + GRID_SIZE // 2, y + GRID_SIZE // 3),
            (x + GRID_SIZE * 2 // 3, y + GRID_SIZE // 2),
            (x + GRID_SIZE // 3, y + GRID_SIZE * 2 // 3)
        ]
        for spot in spots:
            pygame.draw.circle(surface, spot_color, spot, spot_radius)

    def draw_frog(self, surface, x, y):
        """Draw a small frog"""
        # Frog body (circle)
        frog_color = (50, 205, 50)  # Green
        body_radius = int(GRID_SIZE * 0.35)
        body_pos = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        pygame.draw.circle(surface, frog_color, body_pos, body_radius)

        # Frog head
        head_radius = int(GRID_SIZE * 0.25)
        head_pos = (x + GRID_SIZE // 2, y + GRID_SIZE // 4)
        pygame.draw.circle(surface, frog_color, head_pos, head_radius)

        # Frog eyes
        eye_radius = max(2, int(GRID_SIZE * 0.1))
        eye_color = (255, 255, 255)  # White
        left_eye_pos = (head_pos[0] - head_radius // 2,
                        head_pos[1] - head_radius // 2)
        right_eye_pos = (head_pos[0] + head_radius //
                         2, head_pos[1] - head_radius // 2)
        pygame.draw.circle(surface, eye_color, left_eye_pos, eye_radius)
        pygame.draw.circle(surface, eye_color, right_eye_pos, eye_radius)

        # Frog pupils
        pupil_radius = max(1, int(eye_radius // 2))
        pupil_color = (0, 0, 0)  # Black
        pygame.draw.circle(surface, pupil_color, left_eye_pos, pupil_radius)
        pygame.draw.circle(surface, pupil_color, right_eye_pos, pupil_radius)

        # Frog legs
        leg_color = (50, 180, 50)  # Slightly darker green
        # Back legs
        pygame.draw.ellipse(surface, leg_color,
                            (x, y + GRID_SIZE // 2, GRID_SIZE // 3, GRID_SIZE // 3))
        pygame.draw.ellipse(surface, leg_color,
                            (x + GRID_SIZE * 2 // 3, y + GRID_SIZE // 2,
                             GRID_SIZE // 3, GRID_SIZE // 3))

    def draw_bird(self, surface, x, y):
        """Draw a small bird"""
        # Bird body (oval)
        bird_color = (30, 144, 255)  # Blue
        body_width = int(GRID_SIZE * 0.6)
        body_height = int(GRID_SIZE * 0.5)
        body_rect = pygame.Rect(
            x + GRID_SIZE // 4,
            y + GRID_SIZE // 3,
            body_width, body_height
        )
        pygame.draw.ellipse(surface, bird_color, body_rect)

        # Bird head
        head_radius = int(GRID_SIZE * 0.2)
        head_pos = (x + GRID_SIZE * 3 // 4, y + GRID_SIZE // 3)
        pygame.draw.circle(surface, bird_color, head_pos, head_radius)

        # Bird beak
        beak_color = (255, 165, 0)  # Orange
        beak_points = [
            head_pos,
            (head_pos[0] + head_radius, head_pos[1] - head_radius // 2),
            (head_pos[0] + head_radius, head_pos[1] + head_radius // 2)
        ]
        pygame.draw.polygon(surface, beak_color, beak_points)

        # Bird wing
        wing_color = (0, 110, 220)  # Darker blue
        wing_rect = pygame.Rect(
            x + GRID_SIZE // 3,
            y + GRID_SIZE // 4,
            body_width // 2, body_height // 2
        )
        pygame.draw.ellipse(surface, wing_color, wing_rect)

        # Bird eye
        eye_radius = max(1, int(GRID_SIZE * 0.06))
        pygame.draw.circle(surface, (0, 0, 0),
                           (head_pos[0], head_pos[1] - head_radius // 2), eye_radius)

    def draw_fruit(self, surface, x, y):
        """Draw a small piece of fruit (apple)"""
        # Fruit body (circle)
        fruit_color = (255, 0, 0)  # Red
        fruit_radius = int(GRID_SIZE * 0.35)
        fruit_pos = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        pygame.draw.circle(surface, fruit_color, fruit_pos, fruit_radius)

        # Fruit stem
        stem_color = (139, 69, 19)  # Brown
        stem_points = [
            (fruit_pos[0], fruit_pos[1] - fruit_radius),
            (fruit_pos[0], fruit_pos[1] - fruit_radius - GRID_SIZE // 8),
            (fruit_pos[0] + GRID_SIZE // 16,
             fruit_pos[1] - fruit_radius - GRID_SIZE // 6)
        ]
        pygame.draw.lines(surface, stem_color, False, stem_points, 2)

        # Fruit leaf
        leaf_color = (50, 205, 50)  # Green
        leaf_points = [
            stem_points[1],
            (stem_points[1][0] + GRID_SIZE // 6,
             stem_points[1][1] - GRID_SIZE // 10),
            (stem_points[1][0] + GRID_SIZE // 3, stem_points[1][1])
        ]
        pygame.draw.polygon(surface, leaf_color, leaf_points)

        # Fruit highlight (small white ellipse to give 3D effect)
        highlight_color = (255, 220, 220)
        highlight_rect = pygame.Rect(
            fruit_pos[0] - fruit_radius // 2,
            fruit_pos[1] - fruit_radius // 2,
            fruit_radius // 2, fruit_radius // 2
        )
        pygame.draw.ellipse(surface, highlight_color, highlight_rect)

    def draw_bug(self, surface, x, y):
        """Draw a small bug"""
        # Bug body (oval)
        bug_color = (200, 0, 0)  # Red
        body_width = int(GRID_SIZE * 0.6)
        body_height = int(GRID_SIZE * 0.45)
        body_pos = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
        body_rect = pygame.Rect(
            body_pos[0] - body_width // 2,
            body_pos[1] - body_height // 2,
            body_width, body_height
        )
        pygame.draw.ellipse(surface, bug_color, body_rect)

        # Bug spots
        spot_color = (0, 0, 0)  # Black
        spot_radius = max(1, int(GRID_SIZE * 0.08))
        spots = [
            (body_pos[0] - body_width // 3, body_pos[1] - body_height // 3),
            (body_pos[0] + body_width // 3, body_pos[1] - body_height // 3),
            (body_pos[0], body_pos[1]),
            (body_pos[0] - body_width // 3, body_pos[1] + body_height // 3),
            (body_pos[0] + body_width // 3, body_pos[1] + body_height // 3)
        ]
        for spot in spots:
            pygame.draw.circle(surface, spot_color, spot, spot_radius)

        # Bug legs
        leg_color = (50, 50, 50)  # Dark gray
        leg_width = 1
        leg_length = int(GRID_SIZE * 0.25)
        leg_positions = [
            # Left side
            (body_pos[0] - body_width // 2, body_pos[1] - body_height // 3),
            (body_pos[0] - body_width // 2, body_pos[1]),
            (body_pos[0] - body_width // 2, body_pos[1] + body_height // 3),
            # Right side
            (body_pos[0] + body_width // 2, body_pos[1] - body_height // 3),
            (body_pos[0] + body_width // 2, body_pos[1]),
            (body_pos[0] + body_width // 2, body_pos[1] + body_height // 3)
        ]
        for leg_pos in leg_positions:
            if leg_pos[0] < body_pos[0]:  # Left side
                pygame.draw.line(surface, leg_color, leg_pos,
                                 (leg_pos[0] - leg_length, leg_pos[1]), leg_width)
            else:  # Right side
                pygame.draw.line(surface, leg_color, leg_pos,
                                 (leg_pos[0] + leg_length, leg_pos[1]), leg_width)

        # Bug antennae
        antennae_start = (body_pos[0], body_pos[1] - body_height // 2)
        pygame.draw.line(surface, leg_color, antennae_start,
                         (antennae_start[0] - body_width // 4,
                          antennae_start[1] - body_height // 2),
                         leg_width)
        pygame.draw.line(surface, leg_color, antennae_start,
                         (antennae_start[0] + body_width // 4,
                          antennae_start[1] - body_height // 2),
                         leg_width)

    def draw(self, surface):
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE

        # Draw different food types
        if self.food_type == "mouse":
            self.draw_mouse(surface, x, y)
        elif self.food_type == "egg":
            self.draw_egg(surface, x, y)
        elif self.food_type == "frog":
            self.draw_frog(surface, x, y)
        elif self.food_type == "bird":
            self.draw_bird(surface, x, y)
        elif self.food_type == "fruit":
            self.draw_fruit(surface, x, y)
        elif self.food_type == "bug":
            self.draw_bug(surface, x, y)

        # Add a slight glow or highlight around the food
        glow_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.color, glow_rect, 1)
