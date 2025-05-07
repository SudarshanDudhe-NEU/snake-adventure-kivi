import random
from kivy.graphics import Rectangle, Color, Line


class Obstacle:
    def __init__(self, grid_size=20, grid_width=40, grid_height=30):
        self.grid_size = grid_size
        self.grid_width = grid_width
        self.grid_height = grid_height

        # Obstacle types: wall, rocks, spikes
        self.obstacle_types = [
            {"name": "wall", "color": (0.5, 0.3, 0.2, 1), "deadly": True},
            {"name": "rocks", "color": (0.6, 0.6, 0.6, 1), "deadly": True},
            {"name": "spikes", "color": (0.7, 0.1, 0.1, 1), "deadly": True},
            # Non-deadly but will be used for slowdown
            {"name": "mud", "color": (0.4, 0.3, 0.1, 0.7), "deadly": False}
        ]

        # Initialize empty obstacles list
        self.positions = []

        # Level progression - obstacles increase as game progresses
        self.level = 1
        self.max_obstacles = 5  # Start with few obstacles

    def generate_obstacles(self, occupied_positions):
        """Generate obstacles that don't overlap with the snake or food"""
        self.positions = []
        obstacle_count = min(self.max_obstacles,
                             self.level * 2)  # Scale with level

        # Choose a pattern type for this level
        pattern = random.choice(
            ["random", "horizontal", "vertical", "diagonal", "enclosed"])

        if pattern == "random":
            # Random obstacles scattered around
            attempts = 0
            while len(self.positions) < obstacle_count and attempts < 100:
                attempts += 1
                # Keep away from edges
                x = random.randint(2, self.grid_width - 3)
                y = random.randint(2, self.grid_height - 3)

                if (x, y) not in occupied_positions and (x, y) not in self.positions:
                    self.positions.append((x, y))

                    # Sometimes create small clusters
                    if random.random() < 0.3 and len(self.positions) < obstacle_count:
                        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
                                (nx, ny) not in occupied_positions and
                                (nx, ny) not in self.positions and
                                    len(self.positions) < obstacle_count):
                                self.positions.append((nx, ny))

        elif pattern == "horizontal":
            # Horizontal wall with a gap
            y = random.randint(self.grid_height // 4,
                               self.grid_height * 3 // 4)
            wall_start = random.randint(1, self.grid_width // 3)
            gap_start = random.randint(
                wall_start + 3, self.grid_width * 2 // 3)
            gap_width = random.randint(2, 4)
            gap_end = gap_start + gap_width

            for x in range(wall_start, self.grid_width - 1):
                if gap_start <= x < gap_end:  # Skip the gap
                    continue

                if (x, y) not in occupied_positions:
                    self.positions.append((x, y))
                    if len(self.positions) >= obstacle_count:
                        break

        elif pattern == "vertical":
            # Vertical wall with a gap
            x = random.randint(self.grid_width // 4, self.grid_width * 3 // 4)
            wall_start = random.randint(1, self.grid_height // 3)
            gap_start = random.randint(
                wall_start + 3, self.grid_height * 2 // 3)
            gap_width = random.randint(2, 4)
            gap_end = gap_start + gap_width

            for y in range(wall_start, self.grid_height - 1):
                if gap_start <= y < gap_end:  # Skip the gap
                    continue

                if (x, y) not in occupied_positions:
                    self.positions.append((x, y))
                    if len(self.positions) >= obstacle_count:
                        break

        elif pattern == "diagonal":
            # Diagonal line of obstacles
            start_x = random.randint(2, self.grid_width // 3)
            start_y = random.randint(2, self.grid_height // 3)

            for i in range(min(self.grid_width, self.grid_height) - start_x - 2):
                x, y = start_x + i, start_y + i
                if x >= self.grid_width - 2 or y >= self.grid_height - 2:
                    break

                if (x, y) not in occupied_positions and (x, y) not in self.positions:
                    self.positions.append((x, y))

                if len(self.positions) >= obstacle_count:
                    break

        elif pattern == "enclosed":
            # Create a partial enclosure that the snake must navigate
            center_x = self.grid_width // 2
            center_y = self.grid_height // 2

            # Size of the "room"
            room_size = random.randint(5, 8)

            # Build the walls (with a gap)
            gap_side = random.choice(["top", "right", "bottom", "left"])
            gap_pos = random.randint(1, room_size - 2)

            for i in range(room_size):
                # Top wall
                if gap_side != "top" or i != gap_pos:
                    pos = (center_x - room_size//2 +
                           i, center_y + room_size//2)
                    if pos not in occupied_positions and pos not in self.positions:
                        self.positions.append(pos)

                # Bottom wall
                if gap_side != "bottom" or i != gap_pos:
                    pos = (center_x - room_size//2 +
                           i, center_y - room_size//2)
                    if pos not in occupied_positions and pos not in self.positions:
                        self.positions.append(pos)

                # Left wall
                if gap_side != "left" or i != gap_pos:
                    pos = (center_x - room_size//2,
                           center_y - room_size//2 + i)
                    if pos not in occupied_positions and pos not in self.positions:
                        self.positions.append(pos)

                # Right wall
                if gap_side != "right" or i != gap_pos:
                    pos = (center_x + room_size//2,
                           center_y - room_size//2 + i)
                    if pos not in occupied_positions and pos not in self.positions:
                        self.positions.append(pos)

                if len(self.positions) >= obstacle_count:
                    break

        # Assign obstacle types
        self.obstacles = []
        for pos in self.positions:
            # Generally use walls, but sometimes use other types
            obstacle_type = random.choices(
                self.obstacle_types,
                # Walls most common, spikes rarest
                weights=[0.6, 0.2, 0.1, 0.1],
                k=1
            )[0]

            self.obstacles.append({
                "position": pos,
                "type": obstacle_type
            })

    def set_difficulty(self, difficulty):
        """Set the obstacle difficulty"""
        self.difficulty = difficulty

        # Adjust obstacle parameters based on difficulty
        if difficulty == 'easy':
            self.max_obstacles = 3
            self.obstacle_density = 0.5  # Lower means fewer obstacles per level
        elif difficulty == 'normal':
            self.max_obstacles = 5
            self.obstacle_density = 1.0
        elif difficulty == 'hard':
            self.max_obstacles = 7
            self.obstacle_density = 1.5
        elif difficulty == 'expert':
            self.max_obstacles = 10
            self.obstacle_density = 2.0

    def increase_difficulty(self):
        """Increase the difficulty (called when leveling up)"""
        self.level += 1

        # Scale with level and selected difficulty
        base_obstacles = 5
        if hasattr(self, 'difficulty'):
            if self.difficulty == 'easy':
                base_obstacles = 3
            elif self.difficulty == 'normal':
                base_obstacles = 5
            elif self.difficulty == 'hard':
                base_obstacles = 7
            elif self.difficulty == 'expert':
                base_obstacles = 10

        # Calculate max obstacles based on level and difficulty
        density = 1.0
        if hasattr(self, 'obstacle_density'):
            density = self.obstacle_density

        self.max_obstacles = min(
            30, base_obstacles + int(self.level * density))

    def check_collision(self, position):
        """Check if the given position collides with any deadly obstacle"""
        for obstacle in self.obstacles:
            if obstacle["position"] == position and obstacle["type"]["deadly"]:
                return True
        return False

    def draw(self, canvas):
        """Draw obstacles on the canvas"""
        with canvas:
            for obstacle in self.obstacles:
                position = obstacle["position"]
                obstacle_type = obstacle["type"]

                # Base coloring
                Color(*obstacle_type["color"])

                # Draw based on type
                if obstacle_type["name"] == "wall":
                    # Draw a brick wall
                    Rectangle(
                        pos=(position[0] * self.grid_size,
                             position[1] * self.grid_size),
                        size=(self.grid_size, self.grid_size)
                    )

                    # Add brick pattern
                    Color(0.4, 0.2, 0.1)  # Darker brown for lines

                    # Horizontal lines
                    Line(points=[
                        position[0] * self.grid_size, position[1] *
                        self.grid_size + self.grid_size/2,
                        position[0] * self.grid_size + self.grid_size, position[1] *
                        self.grid_size + self.grid_size/2
                    ], width=1)

                    # Vertical lines - staggered for brick effect
                    for i in range(2):
                        offset = (position[1] % 2) * (self.grid_size / 2)
                        Line(points=[
                            position[0] * self.grid_size + offset + i *
                            (self.grid_size / 2), position[1] * self.grid_size,
                            position[0] * self.grid_size + offset + i * (
                                self.grid_size / 2), position[1] * self.grid_size + self.grid_size
                        ], width=1)

                elif obstacle_type["name"] == "rocks":
                    # Draw a cluster of rocks
                    Color(*obstacle_type["color"])

                    # Draw 3-4 small circles to represent rocks
                    for _ in range(4):
                        rx = random.random() * 0.6 + 0.2  # 0.2 - 0.8
                        ry = random.random() * 0.6 + 0.2  # 0.2 - 0.8
                        rs = random.random() * 0.3 + 0.2  # 0.2 - 0.5

                        rock_x = position[0] * self.grid_size + rx * \
                            self.grid_size - rs * self.grid_size / 2
                        rock_y = position[1] * self.grid_size + ry * \
                            self.grid_size - rs * self.grid_size / 2
                        rock_size = rs * self.grid_size

                        Color(obstacle_type["color"][0] * (0.8 + random.random() * 0.4),
                              obstacle_type["color"][1] *
                              (0.8 + random.random() * 0.4),
                              obstacle_type["color"][2] *
                              (0.8 + random.random() * 0.4),
                              obstacle_type["color"][3])

                        Rectangle(
                            pos=(rock_x, rock_y),
                            size=(rock_size, rock_size)
                        )

                elif obstacle_type["name"] == "spikes":
                    # Draw deadly spikes
                    base_y = position[1] * self.grid_size

                    # Draw the base
                    Color(0.5, 0.5, 0.5)
                    Rectangle(
                        pos=(position[0] * self.grid_size, base_y),
                        size=(self.grid_size, self.grid_size * 0.3)
                    )

                    # Draw the spikes
                    Color(*obstacle_type["color"])
                    spike_count = 3
                    spike_width = self.grid_size / spike_count

                    for i in range(spike_count):
                        Line(points=[
                            position[0] * self.grid_size + i *
                            spike_width, base_y + self.grid_size * 0.3,
                            position[0] * self.grid_size +
                            (i + 0.5) * spike_width, base_y + self.grid_size,
                            position[0] * self.grid_size +
                            (i + 1) * spike_width, base_y +
                            self.grid_size * 0.3
                        ], width=2, close=True)

                elif obstacle_type["name"] == "mud":
                    # Draw mud (non-deadly obstacle)
                    Rectangle(
                        pos=(position[0] * self.grid_size,
                             position[1] * self.grid_size),
                        size=(self.grid_size, self.grid_size)
                    )

                    # Add some texture
                    Color(0.35, 0.25, 0.1, 0.5)
                    for _ in range(5):
                        rx = random.random() * 0.8 + 0.1
                        ry = random.random() * 0.8 + 0.1
                        rs = random.random() * 0.3 + 0.1

                        Rectangle(
                            pos=(position[0] * self.grid_size + rx * self.grid_size,
                                 position[1] * self.grid_size + ry * self.grid_size),
                            size=(rs * self.grid_size, rs * self.grid_size)
                        )
