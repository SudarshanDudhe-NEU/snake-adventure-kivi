import random
from kivy.graphics import Ellipse, Rectangle, Color, Line
from kivy.clock import Clock


class Food:
    # Food types with their respective point values
    FOOD_TYPES = [
        {"name": "mouse", "points": 5, "color": (0.6, 0.5, 0.4)},
        {"name": "egg", "points": 1, "color": (0.95, 0.95, 0.8)},
        {"name": "frog", "points": 3, "color": (0.2, 0.8, 0.1)},
        {"name": "bird", "points": 7, "color": (0.7, 0.1, 0.1)},
        {"name": "fruit", "points": 2, "color": (0.9, 0.2, 0.7)},
        {"name": "bug", "points": 1, "color": (0.1, 0.1, 0.1)}
    ]

    def __init__(self, grid_size=20, grid_width=40, grid_height=30):
        self.grid_size = grid_size
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Food properties
        self.position = None
        self.food_type = None
        self.animation_phase = 0
        self.animation = None

        # Generate initial food
        self.generate_new_food()
        self.start_animation()

    def generate_new_food(self, occupied_positions=None):
        """Generate a new random food type and position"""
        if occupied_positions is None:
            occupied_positions = []

        # Choose random position
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in occupied_positions:
                self.position = (x, y)
                break

        # Choose random food type
        self.food_type = random.choice(self.FOOD_TYPES)

    def start_animation(self):
        """Start food animation"""
        self.animation = Clock.schedule_interval(self.animate, 0.15)

    def animate(self, dt):
        """Animate food item"""
        self.animation_phase = (self.animation_phase + 1) % 4

    def respawn(self, occupied_positions):
        """Respawn food at a random position that's not occupied"""
        # Save the old position for animation purposes if needed
        self.old_position = self.position

        # Make sure we have a complete list of occupied positions
        occupied = list(occupied_positions) if occupied_positions else []

        # Add obstacle positions if available
        from .game import SnakeGame
        game = SnakeGame.get_running_instance() if hasattr(
            SnakeGame, 'get_running_instance') else None
        if game and hasattr(game, 'obstacle'):
            for pos in game.obstacle.positions:
                if pos not in occupied:
                    occupied.append(pos)

        # Get all possible positions on the grid
        all_positions = [(x, y)
                         for x in range(self.grid_width)
                         for y in range(self.grid_height)]

        # Remove occupied positions
        available_positions = [
            pos for pos in all_positions if pos not in occupied]

        # Check if we have available positions
        if not available_positions:
            print("WARNING: No available positions for food spawning!")
            # Create one space by choosing a position that's far from the snake head
            # This is a last resort option
            if occupied:
                # Try to find a position far from the snake's head
                snake_head = occupied[0] if occupied else (
                    self.grid_width//2, self.grid_height//2)

                # Sort positions by distance from snake head
                all_positions.sort(key=lambda pos: abs(
                    pos[0] - snake_head[0]) + abs(pos[1] - snake_head[1]), reverse=True)

                # Take the farthest position
                self.position = all_positions[0]
                return

        # Choose a random position from available positions
        self.position = random.choice(available_positions)

        # Choose a random food type
        self.set_random_food_type()

        # Start respawn animation if we have an old position
        if hasattr(self, 'old_position'):
            self.start_respawn_animation()

    def start_respawn_animation(self):
        """Create a visual effect when food respawns"""
        # If running in Kivy context
        try:
            from kivy.animation import Animation
            from kivy.clock import Clock

            # Store the animation time
            self.animating = True

            # Schedule end of animation
            Clock.schedule_once(lambda dt: setattr(
                self, 'animating', False), 0.3)
        except ImportError:
            # Not running in Kivy context
            pass

    def draw(self, canvas):
        """Draw food on the canvas with optional animation"""
        with canvas:
            # Use the food color
            Color(*self.food_type["color"])

            # Draw the food
            size_factor = 1.2 if hasattr(
                self, 'animating') and self.animating else 1.0
            offset = (1.0 - size_factor) * self.grid_size / 2

            Rectangle(
                pos=(
                    self.position[0] * self.grid_size + offset,
                    self.position[1] * self.grid_size + offset
                ),
                size=(
                    self.grid_size * size_factor,
                    self.grid_size * size_factor
                )
            )

    def cleanup(self):
        """Clean up resources"""
        if self.animation:
            self.animation.cancel()
            self.animation = None

    def get_points(self):
        """Return the point value for the current food"""
        return self.food_type["points"]
