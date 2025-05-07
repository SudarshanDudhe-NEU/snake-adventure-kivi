import pygame
import math
from constants import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT


class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.length = 1
        self.direction = pygame.K_RIGHT
        self.color = (0, 255, 0)  # Start with green
        self.score = 0

    def change_color(self, new_color):
        """Update the snake color"""
        self.color = new_color

    def get_head_position(self):
        return self.positions[0]

    def turn(self, new_direction):
        # Prevent the snake from reversing direction
        if (new_direction == pygame.K_UP and self.direction == pygame.K_DOWN) or \
           (new_direction == pygame.K_DOWN and self.direction == pygame.K_UP) or \
           (new_direction == pygame.K_LEFT and self.direction == pygame.K_RIGHT) or \
           (new_direction == pygame.K_RIGHT and self.direction == pygame.K_LEFT):
            return
        self.direction = new_direction

    def move(self):
        head_x, head_y = self.positions[0]

        if self.direction == pygame.K_UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == pygame.K_DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == pygame.K_LEFT:
            new_head = (head_x - 1, head_y)
        else:  # self.direction == pygame.K_RIGHT
            new_head = (head_x + 1, head_y)

        # Wrap around if the snake goes off the screen
        new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)

        # Check if snake collides with itself
        if new_head in self.positions[1:]:
            return True  # Game over

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

        return False  # Game continues

    def grow(self):
        self.length += 1
        self.score += 10

    def draw_eyes(self, surface, head_pos, direction):
        """Draw eyes on the snake's head based on direction"""
        # Calculate eye positions based on direction
        left_eye_pos = None
        right_eye_pos = None
        eye_radius = max(2, GRID_SIZE // 6)
        pupil_radius = max(1, eye_radius // 2)

        # Base eye positions depend on direction
        if direction == pygame.K_RIGHT:
            # Eyes on the right side
            eye_y = head_pos[1] * GRID_SIZE + GRID_SIZE // 3
            left_eye_pos = (head_pos[0] * GRID_SIZE +
                            GRID_SIZE - eye_radius, eye_y)
            right_eye_pos = (
                head_pos[0] * GRID_SIZE + GRID_SIZE - eye_radius, eye_y + GRID_SIZE // 3)
        elif direction == pygame.K_LEFT:
            # Eyes on the left side
            eye_y = head_pos[1] * GRID_SIZE + GRID_SIZE // 3
            left_eye_pos = (head_pos[0] * GRID_SIZE + eye_radius, eye_y)
            right_eye_pos = (head_pos[0] * GRID_SIZE +
                             eye_radius, eye_y + GRID_SIZE // 3)
        elif direction == pygame.K_UP:
            # Eyes on the top
            eye_x = head_pos[0] * GRID_SIZE + GRID_SIZE // 3
            left_eye_pos = (eye_x, head_pos[1] * GRID_SIZE + eye_radius)
            right_eye_pos = (eye_x + GRID_SIZE // 3,
                             head_pos[1] * GRID_SIZE + eye_radius)
        elif direction == pygame.K_DOWN:
            # Eyes on the bottom
            eye_x = head_pos[0] * GRID_SIZE + GRID_SIZE // 3
            left_eye_pos = (
                eye_x, head_pos[1] * GRID_SIZE + GRID_SIZE - eye_radius)
            right_eye_pos = (eye_x + GRID_SIZE // 3,
                             head_pos[1] * GRID_SIZE + GRID_SIZE - eye_radius)

        # Draw the eyes (white part)
        if left_eye_pos and right_eye_pos:
            # Make eyes white with a slight color tint from snake
            eye_color = (220, 220, 220)
            pygame.draw.circle(surface, eye_color, left_eye_pos, eye_radius)
            pygame.draw.circle(surface, eye_color, right_eye_pos, eye_radius)

            # Draw pupils (black dot in the center of each eye)
            pupil_color = (0, 0, 0)
            pygame.draw.circle(surface, pupil_color,
                               left_eye_pos, pupil_radius)
            pygame.draw.circle(surface, pupil_color,
                               right_eye_pos, pupil_radius)

    def draw_tongue(self, surface, head_pos, direction):
        """Draw a flickering tongue for the snake"""
        # Tongue only appears occasionally (based on game tick/time)
        if pygame.time.get_ticks() % 1000 < 200:  # Show tongue for 200ms every second
            tongue_color = (255, 50, 50)  # Bright red

            # Position the tongue based on direction
            if direction == pygame.K_RIGHT:
                # Tongue extends to the right
                tongue_start = (head_pos[0] * GRID_SIZE + GRID_SIZE + GRID_SIZE // 4,
                                head_pos[1] * GRID_SIZE + GRID_SIZE // 2)
                tongue_fork1 = (tongue_start[0] + GRID_SIZE // 2,
                                tongue_start[1] - GRID_SIZE // 6)
                tongue_fork2 = (tongue_start[0] + GRID_SIZE // 2,
                                tongue_start[1] + GRID_SIZE // 6)

            elif direction == pygame.K_LEFT:
                # Tongue extends to the left
                tongue_start = (head_pos[0] * GRID_SIZE - GRID_SIZE // 4,
                                head_pos[1] * GRID_SIZE + GRID_SIZE // 2)
                tongue_fork1 = (tongue_start[0] - GRID_SIZE // 2,
                                tongue_start[1] - GRID_SIZE // 6)
                tongue_fork2 = (tongue_start[0] - GRID_SIZE // 2,
                                tongue_start[1] + GRID_SIZE // 6)

            elif direction == pygame.K_UP:
                # Tongue extends upward
                tongue_start = (head_pos[0] * GRID_SIZE + GRID_SIZE // 2,
                                head_pos[1] * GRID_SIZE - GRID_SIZE // 4)
                tongue_fork1 = (tongue_start[0] - GRID_SIZE // 6,
                                tongue_start[1] - GRID_SIZE // 2)
                tongue_fork2 = (tongue_start[0] + GRID_SIZE // 6,
                                tongue_start[1] - GRID_SIZE // 2)

            elif direction == pygame.K_DOWN:
                # Tongue extends downward
                tongue_start = (head_pos[0] * GRID_SIZE + GRID_SIZE // 2,
                                head_pos[1] * GRID_SIZE + GRID_SIZE + GRID_SIZE // 4)
                tongue_fork1 = (tongue_start[0] - GRID_SIZE // 6,
                                tongue_start[1] + GRID_SIZE // 2)
                tongue_fork2 = (tongue_start[0] + GRID_SIZE // 6,
                                tongue_start[1] + GRID_SIZE // 2)

            # Draw the tongue - a line with a forked end
            pygame.draw.lines(surface, tongue_color, False,
                              [
                                  (head_pos[0] * GRID_SIZE + GRID_SIZE // 2,
                                   head_pos[1] * GRID_SIZE + GRID_SIZE // 2),
                                  tongue_start,
                                  tongue_fork1
                              ], 2)
            pygame.draw.lines(surface, tongue_color, False,
                              [
                                  tongue_start,
                                  tongue_fork2
                              ], 2)

    def draw_scales(self, surface, position, i):
        """Draw scales on the snake body segment"""
        rect = pygame.Rect(position[0] * GRID_SIZE,
                           position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)

        # Base color for the segment
        pygame.draw.rect(surface, self.color, rect)

        # Slightly lighter color for scales
        scale_color = (
            min(255, self.color[0] + 30),
            min(255, self.color[1] + 30),
            min(255, self.color[2] + 30)
        )

        # Slightly darker outline color
        outline_color = (
            max(0, self.color[0] - 50),
            max(0, self.color[1] - 50),
            max(0, self.color[2] - 50)
        )

        # Draw scales differently based on position in the snake
        scale_pattern = (i // 2) % 2  # Alternating pattern
        x = position[0] * GRID_SIZE
        y = position[1] * GRID_SIZE

        # Scale size
        scale_size = max(3, GRID_SIZE // 4)

        # Draw scales in a pattern
        if scale_pattern == 0:
            # Pattern A: diagonal scales
            pygame.draw.ellipse(surface, scale_color,
                                (x + GRID_SIZE // 4, y + GRID_SIZE // 4,
                                 scale_size, scale_size))
            pygame.draw.ellipse(surface, scale_color,
                                (x + GRID_SIZE // 2, y + GRID_SIZE // 2,
                                 scale_size, scale_size))
        else:
            # Pattern B: alternate diagonal
            pygame.draw.ellipse(surface, scale_color,
                                (x + GRID_SIZE // 2, y + GRID_SIZE // 4,
                                 scale_size, scale_size))
            pygame.draw.ellipse(surface, scale_color,
                                (x + GRID_SIZE // 4, y + GRID_SIZE // 2,
                                 scale_size, scale_size))

        # Draw outline
        pygame.draw.rect(surface, outline_color, rect, 1)

    def draw_tail(self, surface, position, prev_position):
        """Draw a more refined, narrower snake tail"""
        # Get the position of the tail segment
        x = position[0] * GRID_SIZE
        y = position[1] * GRID_SIZE

        # Determine the direction of the tail based on the previous segment
        tail_direction = None
        if prev_position[0] > position[0]:  # Tail is to the left of prev segment
            tail_direction = "right"  # Tail points right
        elif prev_position[0] < position[0]:  # Tail is to the right of prev segment
            tail_direction = "left"  # Tail points left
        elif prev_position[1] > position[1]:  # Tail is above prev segment
            tail_direction = "down"  # Tail points down
        else:  # Tail is below prev segment
            tail_direction = "up"  # Tail points up

        # Even narrower tail with smoother transitions
        if tail_direction == "right":
            # Base shape - narrower and more centered
            points = [
                (x + GRID_SIZE//3, y + GRID_SIZE//3),  # Top-left of tail base
                # Bottom-left of tail base
                (x + GRID_SIZE//3, y + GRID_SIZE*2//3),
                # Bottom-right of tail base
                (x + GRID_SIZE*2//3, y + GRID_SIZE*2//3),
                (x + GRID_SIZE*2//3, y + GRID_SIZE//3),  # Top-right of tail base
                # Tip of tail (extended)
                (x + GRID_SIZE + GRID_SIZE//4, y + GRID_SIZE//2)
            ]
            pygame.draw.polygon(surface, self.color, points)

        elif tail_direction == "left":
            # Base shape - narrower and more centered
            points = [
                (x + GRID_SIZE*2//3, y + GRID_SIZE//3),  # Top-right of tail base
                # Bottom-right of tail base
                (x + GRID_SIZE*2//3, y + GRID_SIZE*2//3),
                # Bottom-left of tail base
                (x + GRID_SIZE//3, y + GRID_SIZE*2//3),
                (x + GRID_SIZE//3, y + GRID_SIZE//3),  # Top-left of tail base
                (x - GRID_SIZE//4, y + GRID_SIZE//2)  # Tip of tail (extended)
            ]
            pygame.draw.polygon(surface, self.color, points)

        elif tail_direction == "up":
            # Base shape - narrower and more centered
            points = [
                # Bottom-left of tail base
                (x + GRID_SIZE//3, y + GRID_SIZE*2//3),
                # Bottom-right of tail base
                (x + GRID_SIZE*2//3, y + GRID_SIZE*2//3),
                (x + GRID_SIZE*2//3, y + GRID_SIZE//3),  # Top-right of tail base
                (x + GRID_SIZE//3, y + GRID_SIZE//3),  # Top-left of tail base
                (x + GRID_SIZE//2, y - GRID_SIZE//4)  # Tip of tail (extended)
            ]
            pygame.draw.polygon(surface, self.color, points)

        elif tail_direction == "down":
            # Base shape - narrower and more centered
            points = [
                (x + GRID_SIZE//3, y + GRID_SIZE//3),  # Top-left of tail base
                (x + GRID_SIZE*2//3, y + GRID_SIZE//3),  # Top-right of tail base
                # Bottom-right of tail base
                (x + GRID_SIZE*2//3, y + GRID_SIZE*2//3),
                # Bottom-left of tail base
                (x + GRID_SIZE//3, y + GRID_SIZE*2//3),
                # Tip of tail (extended)
                (x + GRID_SIZE//2, y + GRID_SIZE + GRID_SIZE//4)
            ]
            pygame.draw.polygon(surface, self.color, points)

        # Draw outline for tail
        outline_color = (
            max(0, self.color[0] - 50),
            max(0, self.color[1] - 50),
            max(0, self.color[2] - 50)
        )

        # Draw outline using a polygon for cleaner appearance
        pygame.draw.lines(surface, outline_color, True,
                          points[:-1], 1)  # Base outline
        pygame.draw.line(surface, outline_color,
                         points[2], points[4], 1)  # Bottom to tip
        pygame.draw.line(surface, outline_color,
                         points[3], points[4], 1)  # Top to tip

        # Add a small scale detail
        scale_color = (
            min(255, self.color[0] + 30),
            min(255, self.color[1] + 30),
            min(255, self.color[2] + 30)
        )

        # Position the scale in the middle of the tail base
        scale_size = max(2, GRID_SIZE // 5)
        scale_pos = (x + GRID_SIZE//2 - scale_size//2,
                     y + GRID_SIZE//2 - scale_size//2)

        pygame.draw.ellipse(surface, scale_color,
                            (scale_pos[0], scale_pos[1], scale_size, scale_size))

    def draw_body_segment(self, surface, position, prev_position, next_position):
        """Draw a body segment with improved transitions between segments"""
        x = position[0] * GRID_SIZE
        y = position[1] * GRID_SIZE

        # Base color for the segment
        rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.color, rect)

        # Determine the direction of movement for this segment
        direction_to_prev = None
        if prev_position[0] > position[0]:
            direction_to_prev = "right"
        elif prev_position[0] < position[0]:
            direction_to_prev = "left"
        elif prev_position[1] > position[1]:
            direction_to_prev = "down"
        else:
            direction_to_prev = "up"

        direction_to_next = None
        if next_position[0] > position[0]:
            direction_to_next = "right"
        elif next_position[0] < position[0]:
            direction_to_next = "left"
        elif next_position[1] > position[1]:
            direction_to_next = "down"
        else:
            direction_to_next = "up"

        # Create a smoother transition if there's a bend
        if direction_to_prev != direction_to_next:
            # This is a corner piece - round it to create a smoother bend
            corner_radius = GRID_SIZE // 3

            # Determine which corner to round
            if (direction_to_prev == "right" and direction_to_next == "down") or \
               (direction_to_prev == "down" and direction_to_next == "right"):
                # Round the top-left corner
                pygame.draw.circle(surface, self.color,
                                   (x + corner_radius, y + corner_radius),
                                   corner_radius)
            elif (direction_to_prev == "right" and direction_to_next == "up") or \
                 (direction_to_prev == "up" and direction_to_next == "right"):
                # Round the bottom-left corner
                pygame.draw.circle(surface, self.color,
                                   (x + corner_radius, y +
                                    GRID_SIZE - corner_radius),
                                   corner_radius)
            elif (direction_to_prev == "left" and direction_to_next == "down") or \
                 (direction_to_prev == "down" and direction_to_next == "left"):
                # Round the top-right corner
                pygame.draw.circle(surface, self.color,
                                   (x + GRID_SIZE - corner_radius,
                                    y + corner_radius),
                                   corner_radius)
            elif (direction_to_prev == "left" and direction_to_next == "up") or \
                 (direction_to_prev == "up" and direction_to_next == "left"):
                # Round the bottom-right corner
                pygame.draw.circle(surface, self.color,
                                   (x + GRID_SIZE - corner_radius,
                                    y + GRID_SIZE - corner_radius),
                                   corner_radius)

        # Draw scales
        self.draw_scales_on_segment(
            surface, position, prev_position, next_position)

        # Draw outline
        outline_color = (
            max(0, self.color[0] - 50),
            max(0, self.color[1] - 50),
            max(0, self.color[2] - 50)
        )
        pygame.draw.rect(surface, outline_color, rect, 1)

    def draw_scales_on_segment(self, surface, position, prev_position, next_position):
        """Draw enhanced scales on a body segment"""
        x = position[0] * GRID_SIZE
        y = position[1] * GRID_SIZE

        # Lighter color for scales
        scale_color = (
            min(255, self.color[0] + 30),
            min(255, self.color[1] + 30),
            min(255, self.color[2] + 30)
        )

        # Determine the segment's direction for better scale placement
        is_horizontal = (prev_position[1] == next_position[1])
        is_vertical = (prev_position[0] == next_position[0])

        # Scale size
        scale_size = max(3, GRID_SIZE // 4)
        small_scale = max(2, GRID_SIZE // 5)

        if is_horizontal:
            # Horizontal segment - scales along the top and bottom
            for i in range(3):
                offset_x = GRID_SIZE * (i + 1) // 4
                # Top scales
                pygame.draw.ellipse(surface, scale_color,
                                    (x + offset_x - small_scale//2, y + GRID_SIZE//4 - small_scale//2,
                                     small_scale, small_scale))
                # Bottom scales
                pygame.draw.ellipse(surface, scale_color,
                                    (x + offset_x - small_scale//2, y + GRID_SIZE*3//4 - small_scale//2,
                                     small_scale, small_scale))

        elif is_vertical:
            # Vertical segment - scales along the left and right
            for i in range(3):
                offset_y = GRID_SIZE * (i + 1) // 4
                # Left scales
                pygame.draw.ellipse(surface, scale_color,
                                    (x + GRID_SIZE//4 - small_scale//2, y + offset_y - small_scale//2,
                                     small_scale, small_scale))
                # Right scales
                pygame.draw.ellipse(surface, scale_color,
                                    (x + GRID_SIZE*3//4 - small_scale//2, y + offset_y - small_scale//2,
                                     small_scale, small_scale))

        else:
            # Corner piece - fewer scales to avoid visual clutter
            pygame.draw.ellipse(surface, scale_color,
                                (x + GRID_SIZE//2 - small_scale//2, y + GRID_SIZE//2 - small_scale//2,
                                 small_scale, small_scale))

    def draw(self, surface):
        """Draw the complete snake with all improvements"""
        # Draw the body segments
        for i, position in enumerate(self.positions):
            if i == 0:  # This is the head
                # Draw a rounded rectangle for the head
                rect = pygame.Rect(
                    position[0] * GRID_SIZE, position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)

                # First draw the basic rectangle
                pygame.draw.rect(surface, self.color, rect)

                # Draw rounded front based on direction
                if self.direction == pygame.K_RIGHT:
                    pygame.draw.circle(surface, self.color,
                                       (position[0] * GRID_SIZE + GRID_SIZE,
                                        position[1] * GRID_SIZE + GRID_SIZE // 2),
                                       GRID_SIZE // 2)
                elif self.direction == pygame.K_LEFT:
                    pygame.draw.circle(surface, self.color,
                                       (position[0] * GRID_SIZE,
                                        position[1] * GRID_SIZE + GRID_SIZE // 2),
                                       GRID_SIZE // 2)
                elif self.direction == pygame.K_UP:
                    pygame.draw.circle(surface, self.color,
                                       (position[0] * GRID_SIZE + GRID_SIZE // 2,
                                        position[1] * GRID_SIZE),
                                       GRID_SIZE // 2)
                elif self.direction == pygame.K_DOWN:
                    pygame.draw.circle(surface, self.color,
                                       (position[0] * GRID_SIZE + GRID_SIZE // 2,
                                        position[1] * GRID_SIZE + GRID_SIZE),
                                       GRID_SIZE // 2)

                # Draw outline for head - slightly darker than the main color
                outline_color = (max(0, self.color[0] - 50),
                                 max(0, self.color[1] - 50),
                                 max(0, self.color[2] - 50))
                pygame.draw.rect(surface, outline_color, rect, 1)

                # Draw the eyes and tongue
                self.draw_eyes(surface, position, self.direction)
                # New tongue animation
                self.draw_tongue(surface, position, self.direction)

            elif i == len(self.positions) - 1 and len(self.positions) > 1:  # This is the tail
                # Draw the improved tail
                prev_position = self.positions[i - 1]
                self.draw_tail(surface, position, prev_position)

            else:  # Body segment
                # Get previous and next segments for better body transitions
                prev_position = self.positions[i - 1]
                next_position = self.positions[i + 1]
                # Draw the improved body segment with transitions
                self.draw_body_segment(
                    surface, position, prev_position, next_position)
