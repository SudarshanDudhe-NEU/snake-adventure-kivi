from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.clock import Clock
from collections import deque
import math


class Snake:
    def __init__(self, grid_size=20, grid_width=40, grid_height=30):
        # Initialize with game grid parameters
        self.grid_size = grid_size
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Start in the middle of the screen
        start_x = grid_width // 2
        start_y = grid_height // 2

        # Initialize with 3 segments
        self.body = [(start_x, start_y), (start_x-1, start_y),
                     (start_x-2, start_y)]
        self.direction = (1, 0)  # Initial direction: moving right
        self.grow = False
        self.is_alive = True

        # Visual enhancements
        self.tongue_out = False
        self.tongue_animation = None

        # Color tracking - each segment gets its own color
        # Start with a default green gradient
        self.segment_colors = deque([
            (0, 0.8, 0, 1),  # Head (bright green)
            (0, 0.7, 0, 1),  # First body segment
            (0, 0.6, 0, 1)   # Second body segment
        ])

        # Default head color (if no food eaten yet)
        self.default_head_color = (0, 0.9, 0, 1)
        self.default_body_color = (0, 0.7, 0, 1)

        # Keep track of last eaten food color
        self.last_food_color = None

        # Start tongue animation
        self.start_tongue_animation()

        # Add smooth movement
        self.smooth_movement = True
        self.visual_positions = []  # Stores actual drawing positions

        # Initialize visual positions to match grid positions
        for pos in self.body:
            self.visual_positions.append(
                (pos[0] * grid_size, pos[1] * grid_size))

        # Movement interpolation - higher = smoother but slower visually
        self.move_interpolation_steps = 5
        self.current_step = 0

    def start_tongue_animation(self):
        # Animate tongue every 0.5 seconds
        self.tongue_animation = Clock.schedule_interval(
            self.toggle_tongue, 0.5)

    def toggle_tongue(self, dt):
        self.tongue_out = not self.tongue_out

    def move(self):
        """Move the snake in the current direction"""
        # Get current head position
        head = self.body[0]

        # Calculate new head position based on direction
        new_head = (
            (head[0] + self.direction[0]) % self.grid_width,
            (head[1] + self.direction[1]) % self.grid_height
        )

        # Check for collision with self (except when growing)
        # This check should exclude the last tail segment (which will be removed unless growing)
        check_body = self.body[:-1] if not self.grow else self.body
        if new_head in check_body:
            self.is_alive = False
            return

        # Add new head to the front of the body
        self.body.insert(0, new_head)

        # Add new visual position
        new_visual_head = (new_head[0] * self.grid_size,
                           new_head[1] * self.grid_size)
        self.visual_positions.insert(0, new_visual_head)

        # If not growing, remove the tail segment
        if not self.grow:
            self.body.pop()
            if self.visual_positions:
                self.visual_positions.pop()
        else:
            # Reset the grow flag after growing
            self.grow = False

            # Add a new color to the segment_colors deque for the new segment
            if self.last_food_color:
                # Mix the food color with default color
                new_color = self.mix_colors(
                    self.last_food_color, (0, 0.7, 0, 1), 0.7)
                self.segment_colors.appendleft(new_color)

    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        opposite_direction = (-self.direction[0], -self.direction[1])
        if new_direction != opposite_direction:
            self.direction = new_direction

    def grow_snake(self):
        """Grow the snake by setting the grow flag"""
        # When this flag is set, the tail won't be removed on the next move,
        # effectively growing the snake by one segment
        self.grow = True

    def add_food_color(self, food_color):
        """Update snake colors based on the food eaten"""
        # Mix the food color with our default color to create a new head color
        # 70% food color, 30% snake color
        mixed_color = self.mix_colors(food_color, self.default_head_color, 0.7)

        # Insert the new color at the head position
        self.segment_colors.appendleft(mixed_color)

        # Save the last food color
        self.last_food_color = food_color

        # Ensure we have the right number of colors
        while len(self.segment_colors) < len(self.body):
            # Gradually fade back to default color
            new_color = self.mix_colors(
                self.segment_colors[-1],
                self.default_body_color,
                0.8  # 80% current color, 20% default
            )
            self.segment_colors.append(new_color)

        # Trim excess colors if needed
        while len(self.segment_colors) > len(self.body):
            self.segment_colors.pop()

    def mix_colors(self, color1, color2, ratio=0.5):
        """Mix two colors together with the given ratio"""
        # Ensure both colors have 4 components (RGBA)
        if len(color1) == 3:  # If RGB provided, add alpha of 1.0
            color1 = (color1[0], color1[1], color1[2], 1.0)

        if color2 and len(color2) == 3:  # If RGB provided, add alpha of 1.0
            color2 = (color2[0], color2[1], color2[2], 1.0)
        elif not color2:
            color2 = (0, 0.7, 0, 1)  # Default green with alpha

        r1, g1, b1, a1 = color1
        r2, g2, b2, a2 = color2

        # Mix RGB values according to ratio
        r = r1 * ratio + r2 * (1 - ratio)
        g = g1 * ratio + g2 * (1 - ratio)
        b = b1 * ratio + b2 * (1 - ratio)
        a = a1 * ratio + a2 * (1 - ratio)

        return (r, g, b, a)

    def check_collision(self, position):
        # Check if the head collides with the body
        return position in self.body[1:]

    def get_head_position(self):
        return self.body[0]

    def draw_tapered_segment(self, canvas, pos, size_factor=1.0, color=None):
        """Draw a segment with the specified size factor and color"""
        adjusted_size = self.grid_size * size_factor
        pos_x = pos[0] * self.grid_size + (self.grid_size - adjusted_size) / 2
        pos_y = pos[1] * self.grid_size + (self.grid_size - adjusted_size) / 2

        with canvas:
            if color:
                Color(*color)
            Rectangle(
                pos=(pos_x, pos_y),
                size=(adjusted_size, adjusted_size)
            )

    def update_visual_positions(self, interpolation_factor):
        """Update visual positions for smooth movement"""
        if not self.smooth_movement or len(self.visual_positions) != len(self.body):
            return

        # Update visual positions to move toward grid positions
        for i, (grid_pos, visual_pos) in enumerate(zip(self.body, self.visual_positions)):
            target_x = grid_pos[0] * self.grid_size
            target_y = grid_pos[1] * self.grid_size

            current_x, current_y = visual_pos

            # Move visual position toward grid position
            new_x = current_x + (target_x - current_x) * interpolation_factor
            new_y = current_y + (target_y - current_y) * interpolation_factor

            self.visual_positions[i] = (new_x, new_y)

    def draw(self, canvas):
        """Draw the snake on the canvas with smooth movement"""
        # Use visual positions if smooth movement is enabled
        positions_to_use = self.visual_positions if self.smooth_movement else [
            (pos[0] * self.grid_size, pos[1] * self.grid_size) for pos in self.body
        ]

        with canvas:
            # Draw snake body with colors based on food consumption
            for i, pos in enumerate(positions_to_use):
                if i == 0:  # Skip head, we'll draw it separately
                    continue

                # Get the color for this segment
                if i < len(self.segment_colors):
                    segment_color = self.segment_colors[i]
                else:
                    # Default gradient if we don't have enough colors
                    intensity = max(0.3, 0.7 - (i / len(self.body)) * 0.4)
                    segment_color = (0, intensity, 0, 1)

                # Apply a gradient effect for a smoother appearance
                # Calculate taper factor - smaller segments near the tail
                taper_factor = max(0.6, 1.0 - (i / len(self.body)) * 0.4)

                # Draw the segment with its color
                Color(*segment_color)
                Ellipse(
                    pos=(pos[0] + (self.grid_size * (1-taper_factor))/2,
                         pos[1] + (self.grid_size * (1-taper_factor))/2),
                    size=(self.grid_size * taper_factor,
                          self.grid_size * taper_factor)
                )

            # Draw snake head
            if positions_to_use:
                head_pos = positions_to_use[0]
                head_color = self.segment_colors[0] if self.segment_colors else self.default_head_color

                # Draw head at visual position
                Color(*head_color)
                Ellipse(
                    pos=(head_pos[0], head_pos[1]),
                    size=(self.grid_size, self.grid_size)
                )

                # Head highlight for 3D effect
                r, g, b, a = head_color
                highlight_color = (
                    min(1.0, r*1.2), min(1.0, g*1.2), min(1.0, b*1.2), 0.5)
                Color(*highlight_color)
                highlight_size = self.grid_size * 0.6
                highlight_offset = self.grid_size * 0.1
                Ellipse(
                    pos=(head_pos[0] + highlight_offset,
                         head_pos[1] + highlight_offset),
                    size=(highlight_size, highlight_size)
                )

                # Draw eyes
                eye_size = self.grid_size * 0.25
                eye_offset = self.grid_size * 0.25

                # Eye positions depend on direction
                left_eye_pos = None
                right_eye_pos = None

                if self.direction == (1, 0):  # Right
                    left_eye_pos = (head_pos[0] + self.grid_size - eye_offset - eye_size,
                                    head_pos[1] + self.grid_size - eye_offset - eye_size)
                    right_eye_pos = (head_pos[0] + self.grid_size - eye_offset - eye_size,
                                     head_pos[1] + eye_offset)
                elif self.direction == (-1, 0):  # Left
                    left_eye_pos = (head_pos[0] + eye_offset,
                                    head_pos[1] + eye_offset)
                    right_eye_pos = (head_pos[0] + eye_offset,
                                     head_pos[1] + self.grid_size - eye_offset - eye_size)
                elif self.direction == (0, 1):  # Up
                    left_eye_pos = (head_pos[0] + eye_offset,
                                    head_pos[1] + self.grid_size - eye_offset - eye_size)
                    right_eye_pos = (head_pos[0] + self.grid_size - eye_offset - eye_size,
                                     head_pos[1] + self.grid_size - eye_offset - eye_size)
                elif self.direction == (0, -1):  # Down
                    left_eye_pos = (head_pos[0] + eye_offset,
                                    head_pos[1] + eye_offset)
                    right_eye_pos = (head_pos[0] + self.grid_size - eye_offset - eye_size,
                                     head_pos[1] + eye_offset)

                # Draw the eyes
                if left_eye_pos and right_eye_pos:
                    # White part of eyes
                    Color(1, 1, 1, 1)
                    Ellipse(pos=left_eye_pos, size=(eye_size, eye_size))
                    Ellipse(pos=right_eye_pos, size=(eye_size, eye_size))

                    # Pupils - make them slightly colored based on food
                    pupil_color = (0, 0, 0, 1)  # Default black
                    if self.last_food_color:
                        # Handle both RGB and RGBA food colors
                        if len(self.last_food_color) == 3:
                            r, g, b = self.last_food_color
                            pupil_color = (r * 0.2, g * 0.2, b * 0.2, 1)
                        else:
                            r, g, b, _ = self.last_food_color
                            pupil_color = (r * 0.2, g * 0.2, b * 0.2, 1)

                    Color(*pupil_color)
                    pupil_size = eye_size * 0.6
                    pupil_offset = (eye_size - pupil_size) / 2
                    Ellipse(pos=(left_eye_pos[0] + pupil_offset, left_eye_pos[1] + pupil_offset),
                            size=(pupil_size, pupil_size))
                    Ellipse(pos=(right_eye_pos[0] + pupil_offset, right_eye_pos[1] + pupil_offset),
                            size=(pupil_size, pupil_size))

                # Draw tongue - match tongue color to head color slightly
                if self.tongue_out:
                    # Make tongue reddish but with a hint of the snake's color
                    r, g, b, _ = head_color  # Head color should always be RGBA at this point
                    tongue_color = (0.9 + r * 0.1, 0.1 + g *
                                    0.05, 0.1 + b * 0.05, 1)
                    Color(*tongue_color)
                    tongue_width = self.grid_size * 0.1
                    tongue_length = self.grid_size * 0.5
                    fork_length = self.grid_size * 0.25

                    # Tongue base position depends on direction
                    tongue_base_x = head_pos[0] + self.grid_size / 2
                    tongue_base_y = head_pos[1] + self.grid_size / 2

                    if self.direction == (1, 0):  # Right
                        # Tongue straight part
                        Line(points=[tongue_base_x, tongue_base_y,
                                     tongue_base_x + tongue_length, tongue_base_y],
                             width=tongue_width)

                        # Forked part
                        Line(points=[tongue_base_x + tongue_length, tongue_base_y,
                                     tongue_base_x + tongue_length + fork_length, tongue_base_y + fork_length],
                             width=tongue_width)
                        Line(points=[tongue_base_x + tongue_length, tongue_base_y,
                                     tongue_base_x + tongue_length + fork_length, tongue_base_y - fork_length],
                             width=tongue_width)

                    elif self.direction == (-1, 0):  # Left
                        Line(points=[tongue_base_x, tongue_base_y,
                                     tongue_base_x - tongue_length, tongue_base_y],
                             width=tongue_width)
                        Line(points=[tongue_base_x - tongue_length, tongue_base_y,
                                     tongue_base_x - tongue_length - fork_length, tongue_base_y + fork_length],
                             width=tongue_width)
                        Line(points=[tongue_base_x - tongue_length, tongue_base_y,
                                     tongue_base_x - tongue_length - fork_length, tongue_base_y - fork_length],
                             width=tongue_width)

                    elif self.direction == (0, 1):  # Up
                        Line(points=[tongue_base_x, tongue_base_y,
                                     tongue_base_x, tongue_base_y + tongue_length],
                             width=tongue_width)
                        Line(points=[tongue_base_x, tongue_base_y + tongue_length,
                                     tongue_base_x + fork_length, tongue_base_y + tongue_length + fork_length],
                             width=tongue_width)
                        Line(points=[tongue_base_x, tongue_base_y + tongue_length,
                                     tongue_base_x - fork_length, tongue_base_y + tongue_length + fork_length],
                             width=tongue_width)

                    elif self.direction == (0, -1):  # Down
                        Line(points=[tongue_base_x, tongue_base_y,
                                     tongue_base_x, tongue_base_y - tongue_length],
                             width=tongue_width)
                        Line(points=[tongue_base_x, tongue_base_y - tongue_length,
                                     tongue_base_x + fork_length, tongue_base_y - tongue_length - fork_length],
                             width=tongue_width)
                        Line(points=[tongue_base_x, tongue_base_y - tongue_length,
                                     tongue_base_x - fork_length, tongue_base_y - tongue_length - fork_length],
                             width=tongue_width)
