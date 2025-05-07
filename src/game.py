from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics.instructions import InstructionGroup
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
import os
import datetime
import random
from .snake import Snake
from .food import Food
from .obstacle import Obstacle


class SnakeGame(Widget):
    # Class variable to store the instance
    _instance = None

    def __init__(self, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)
        # Store reference to instance
        SnakeGame._instance = self

        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Configurable game settings
        self.config_store = JsonStore(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'config.json'))

        # Load or set default game configuration
        self.load_game_config()

        # Game settings
        self.grid_size = self.config['grid_size']
        self.grid_width = Window.width // self.grid_size
        self.grid_height = Window.height // self.grid_size

        # Set a slower default game speed (was probably 10-15 FPS)
        self.game_speed = 7  # Slower default speed

        # If there's already a config value, use that instead
        if 'game_speed' in self.config:
            self.game_speed = self.config['game_speed']
        else:
            # Update the config with our new default
            self.config['game_speed'] = self.game_speed
            self.save_game_config()

        # Rest of your initialization code...

        # Update the speed settings in your settings menu if present
        self.speed_settings = [
            ('Very Slow', 3), ('Slow', 5), ('Normal', 7), ('Fast', 10), ('Insane', 15)]

        # Schedule updates at the configured speed
        self.update_event = Clock.schedule_interval(
            self.update, 1.0 / self.game_speed)

        # Score tracking enhancements
        self.score = 0
        self.high_score = self.load_high_score()
        self.combo_counter = 0
        self.combo_timer = None
        self.combo_multiplier = 1.0
        self.points_history = []
        self.score_store = JsonStore(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'scores.json'))

        # Rest of your initialization code...
        self.snake = Snake(self.grid_size, self.grid_width, self.grid_height)
        self.food = Food(self.grid_size, self.grid_width, self.grid_height)
        self.obstacle = Obstacle(
            self.grid_size, self.grid_width, self.grid_height)

        # Generate initial obstacles
        self.obstacle.generate_obstacles(
            self.snake.body + [self.food.position])

        # Game state
        self.level = 1
        self.level_threshold = 5  # Score needed to advance level
        self.game_over = False
        self.paused = False

        # Add last eaten food display
        self.last_food_name = None

        # Setup keyboard control
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Enhanced score label with high score
        self.score_label = Label(
            text=f"Score: {self.score} | High Score: {self.high_score}",
            font_size='18sp',
            pos=(10, Window.height - 30),
            color=(1, 1, 1, 1)  # White text
        )
        self.add_widget(self.score_label)

        # Combo multiplier label
        self.combo_label = Label(
            text="",
            font_size='16sp',
            pos=(10, Window.height - 55),
            color=(1, 0.8, 0, 1)  # Gold color
        )
        self.add_widget(self.combo_label)

        # Food info label
        self.food_label = Label(
            text="",
            font_size='16sp',
            pos=(10, Window.height - 80),
            color=(0.9, 0.9, 0.5, 1)  # Light yellow
        )
        self.add_widget(self.food_label)

        # Level label
        self.level_label = Label(
            text=f"Level: {self.level}",
            font_size='18sp',
            pos=(Window.width - 100, Window.height - 30),
            color=(0.7, 0.7, 1, 1)  # Light blue
        )
        self.add_widget(self.level_label)

        # Score history visual (last 5 scores)
        self.score_history_widget = BoxLayout(
            orientation='horizontal',
            spacing=dp(5),
            size_hint=(None, None),
            size=(dp(150), dp(30)),
            pos=(Window.width - 160, Window.height - 60)
        )
        self.add_widget(self.score_history_widget)

        # Schedule the update at the configured speed
        self.update_event = Clock.schedule_interval(
            self.update, 1.0 / self.game_speed)

        # Add a settings button in the corner
        settings_button = Button(
            text="⚙️",
            font_size='22sp',
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            pos=(Window.width - 50, 10),
            background_color=(0.3, 0.3, 0.3, 0.7)
        )
        settings_button.bind(on_press=lambda x: self.open_settings())
        self.add_widget(settings_button)

    @classmethod
    def get_running_instance(cls):
        """Get the currently running game instance"""
        return cls._instance

    def load_high_score(self):
        """Load high score from storage"""
        try:
            if self.score_store.exists('high_score'):
                return self.score_store.get('high_score')['value']
        except:
            pass
        return 0

    def save_high_score(self):
        """Save high score to storage"""
        try:
            self.score_store.put('high_score', value=self.high_score)
        except:
            pass

    def save_score_history(self):
        """Save current score to history"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Get existing history or create new
            if self.score_store.exists('history'):
                history = self.score_store.get('history')['scores']
            else:
                history = []

            # Add new score entry
            history.append({
                'score': self.score,
                'level': self.level,
                'timestamp': timestamp
            })

            # Keep only last 10 scores
            if len(history) > 10:
                history = history[-10:]

            # Save updated history
            self.score_store.put('history', scores=history)
        except:
            pass

    def update_combo_multiplier(self, reset=False):
        """Update the combo multiplier and UI"""
        if reset:
            self.combo_counter = 0
            self.combo_multiplier = 1.0
            self.combo_label.text = ""
            if self.combo_timer:
                self.combo_timer.cancel()
                self.combo_timer = None
            return

        # Increase combo counter
        self.combo_counter += 1

        # Calculate multiplier (caps at 3.0x)
        if self.combo_counter >= 5:
            self.combo_multiplier = min(
                3.0, 1.0 + (self.combo_counter - 5) * 0.2 + 1.0)
        elif self.combo_counter >= 3:
            self.combo_multiplier = 2.0
        else:
            self.combo_multiplier = 1.0

        # Update combo label with animation
        self.combo_label.text = f"Combo: x{self.combo_multiplier:.1f}"

        if self.combo_multiplier > 1.0:
            # Flash the combo text for visual feedback
            self.combo_label.color = (1, 0.6, 0, 1)  # Bright gold
            anim = Animation(color=(1, 0.8, 0, 1), duration=0.3)
            anim.start(self.combo_label)

            # Make label slightly larger then back to normal
            self.combo_label.font_size = '18sp'
            size_anim = Animation(font_size='16sp', duration=0.3)
            size_anim.start(self.combo_label)

        # Reset combo timer
        if self.combo_timer:
            self.combo_timer.cancel()

        # Combo expires after 3 seconds
        self.combo_timer = Clock.schedule_once(
            lambda dt: self.expire_combo(), 3.0)

    def expire_combo(self):
        """Reset combo when timer expires"""
        self.update_combo_multiplier(reset=True)

    def update_score_history_visual(self, points):
        """Update the visual display of recent points scored"""
        # Add the points to history
        self.points_history.append(points)
        if len(self.points_history) > 5:
            self.points_history.pop(0)

        # Recreate the visual display
        self.score_history_widget.clear_widgets()

        for point in self.points_history:
            # Create a label for each recent score
            point_label = Label(
                text=f"+{point}",
                font_size='14sp',
                color=self.get_points_color(point),
                size_hint=(None, None),
                size=(dp(30), dp(30))
            )
            self.score_history_widget.add_widget(point_label)

    def get_points_color(self, points):
        """Return a color based on points value"""
        if points >= 15:  # Exceptional score
            return (1, 0.1, 1, 1)  # Purple
        elif points >= 10:  # Very good score
            return (1, 0.1, 0.1, 1)  # Red
        elif points >= 5:  # Good score
            return (1, 0.8, 0, 1)  # Gold
        else:  # Basic score
            return (0, 0.8, 0, 1)  # Green

    # Fix for the game ending when eating food

    def update(self, dt):
        if self.paused or self.game_over:
            return

        # Update snake's visual positions for smooth movement
        # Use a fixed interpolation factor (0.2 = smooth, 1.0 = instant)
        self.snake.update_visual_positions(0.2)

        # Only move the snake on certain frames for smoother animation
        self.current_frame = getattr(self, 'current_frame', 0) + 1
        movement_interval = 3  # Move every 3rd frame

        if self.current_frame % movement_interval == 0:
            # Move the snake
            self.snake.move()

            # Get the head position AFTER moving
            head_pos = self.snake.get_head_position()

            # First check if food was eaten (before checking death conditions)
            food_eaten = False
            if head_pos == self.food.position:
                food_eaten = True
                # Handle food consumption
                self.handle_food_consumed()

            # Check for death conditions ONLY if we didn't eat food
            # This prevents false collision detection when the snake grows
            if not food_eaten:
                # Check for collision with self
                if not self.snake.is_alive:
                    self.game_over = True
                    self.display_game_over()
                    return

                # Check for collision with obstacles
                if self.obstacle.check_collision(head_pos):
                    self.snake.is_alive = False
                    self.game_over = True
                    self.display_game_over()
                    return

        # Redraw everything every frame for smooth animation
        self.canvas.clear()
        self.draw_grid()
        self.obstacle.draw(self.canvas)
        self.food.draw(self.canvas)
        self.snake.draw(self.canvas)

    # Add this new method to handle food consumption logic
    def handle_food_consumed(self):
        """Handle all logic when food is consumed"""
        # Get base points for this food
        base_points = self.food.get_points()

        # Apply combo multiplier
        actual_points = int(base_points * self.combo_multiplier)

        # Update combo system
        self.update_combo_multiplier()

        # Add points to score
        self.score += actual_points

        # Update score history visual
        self.update_score_history_visual(actual_points)

        # Check for high score
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            # Visual cue for new high score
            high_score_notif = Label(
                text="NEW HIGH SCORE!",
                font_size='24sp',
                color=(1, 0.8, 0, 1),
                center_x=Window.width/2,
                center_y=Window.height/2 + 50
            )
            self.add_widget(high_score_notif)
            anim = Animation(opacity=0, duration=1.5)
            anim.bind(
                on_complete=lambda *args: self.remove_widget(high_score_notif))
            anim.start(high_score_notif)

        # Update score label
        self.score_label.text = f"Score: {self.score} | High Score: {self.high_score}"

        # Update food info label with multiplier info
        self.last_food_name = self.food.food_type["name"]
        multiplier_text = f" x{self.combo_multiplier:.1f}" if self.combo_multiplier > 1 else ""
        self.food_label.text = f"Yum! {self.last_food_name.capitalize()} +{actual_points} points{multiplier_text}"

        # Show animation for the food label
        self.food_label.opacity = 1
        food_anim = Animation(opacity=0, duration=2.0)
        food_anim.start(self.food_label)

        # Update snake color based on food eaten
        self.snake.add_food_color(self.food.food_type["color"])

        # Grow snake BEFORE respawning food to include new head in occupied positions
        self.snake.grow_snake()

        # Collect ALL occupied positions to avoid spawning food inside snake or obstacles
        occupied_positions = self.snake.body.copy() + self.obstacle.positions.copy()

        # Debug info to help diagnose issues
        print(f"Snake body length: {len(self.snake.body)}")
        print(f"Obstacle count: {len(self.obstacle.positions)}")
        print(f"Total occupied positions: {len(occupied_positions)}")

        # Respawn food and avoid ALL obstacles
        self.food.respawn(occupied_positions)

        # Verify food position isn't inside snake or obstacles
        if self.food.position in self.snake.body or self.food.position in self.obstacle.positions:
            print(
                f"WARNING: Food respawned at occupied position: {self.food.position}")
            # Try again with extra care
            available = [(x, y)
                         for x in range(self.grid_width)
                         for y in range(self.grid_height)
                         if (x, y) not in occupied_positions]

            if available:
                self.food.position = random.choice(available)

        # Check if player advances to the next level
        if self.score >= self.level * self.level_threshold:
            self.level_up()

    # Enhanced game over and restart functionality

    def display_game_over(self):
        """Display a visually appealing game over screen with animations and extra details"""
        # Save score to history
        self.save_score_history()

        # Create semi-transparent dark overlay
        self.game_over_bg = InstructionGroup()
        self.game_over_bg.add(Color(0, 0, 0, 0.8))  # Dark overlay
        self.game_over_bg.add(
            Rectangle(pos=(0, 0), size=(Window.width, Window.height)))
        self.canvas.add(self.game_over_bg)

        # Create container for all game over elements
        self.game_over_container = FloatLayout()

        # Create main layout
        game_over_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint=(0.5, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Show different messages based on score
        if self.score > self.high_score * 0.8 and self.score > 10:
            message = "IMPRESSIVE!"
            color = (0.2, 1, 0.2, 1)  # Green
        elif self.level > 3:
            message = "WELL PLAYED!"
            color = (1, 0.8, 0, 1)  # Gold
        else:
            message = "GAME OVER"
            color = (1, 0, 0, 1)  # Red

        # Title with dynamic message
        game_over_title = Label(
            text=message,
            font_size='46sp',
            color=color,
            size_hint=(1, 0.2)
        )
        game_over_layout.add_widget(game_over_title)

        # Death cause
        death_message = "You crashed into yourself!" if not self.snake.is_alive else "You hit an obstacle!"
        death_label = Label(
            text=death_message,
            font_size='22sp',
            color=(1, 0.5, 0.5, 1),
            size_hint=(1, 0.15)
        )
        game_over_layout.add_widget(death_label)

        # Final score with styling
        final_score = Label(
            text=f"Final Score: {self.score}",
            font_size='32sp',
            color=(1, 0.8, 0, 1),
            size_hint=(1, 0.15)
        )
        game_over_layout.add_widget(final_score)

        # High score with indication if beaten
        is_new_high = self.score >= self.high_score
        high_score_text = f"NEW HIGH SCORE!" if is_new_high else f"High Score: {self.high_score}"
        high_score = Label(
            text=high_score_text,
            font_size='24sp',
            color=(1, 1, 0, 1) if is_new_high else (0.8, 0.8, 1, 1),
            size_hint=(1, 0.12)
        )
        game_over_layout.add_widget(high_score)

        # Snake length
        snake_length = Label(
            text=f"Snake Length: {len(self.snake.body)} segments",
            font_size='20sp',
            color=(0.6, 1, 0.6, 1),
            size_hint=(1, 0.12)
        )
        game_over_layout.add_widget(snake_length)

        # Level reached
        level_reached = Label(
            text=f"Level Reached: {self.level}",
            font_size='20sp',
            color=(0.7, 0.7, 1, 1),
            size_hint=(1, 0.12)
        )
        game_over_layout.add_widget(level_reached)

        # Button container
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5}
        )

        # Restart button
        restart_button = Button(
            text="RESTART",
            font_size='20sp',
            background_color=(0.2, 0.7, 0.2, 1),
            size_hint=(0.5, 1)
        )
        restart_button.bind(on_press=lambda x: self.reset_game())
        button_layout.add_widget(restart_button)

        # Quit button
        quit_button = Button(
            text="QUIT",
            font_size='20sp',
            background_color=(0.7, 0.2, 0.2, 1),
            size_hint=(0.5, 1)
        )
        quit_button.bind(on_press=lambda x: App.get_running_app().stop())
        button_layout.add_widget(quit_button)

        game_over_layout.add_widget(button_layout)

        # Keyboard shortcut reminder
        keyboard_hint = Label(
            text="Press 'R' to restart | Press 'Q' to quit",
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1),
            size_hint=(1, 0.1)
        )
        game_over_layout.add_widget(keyboard_hint)

        # Add the main layout to the container
        self.game_over_container.add_widget(game_over_layout)

        # Add death animation elements - falling segments
        self.create_death_animation()

        # Add to game
        self.add_widget(self.game_over_container)

        # Animate in the game over screen
        game_over_layout.opacity = 0
        game_over_layout.pos_hint = {'center_x': 0.5, 'center_y': 0.6}

        # Sequence of animations
        anim1 = Animation(opacity=1, pos_hint={
                          'center_x': 0.5, 'center_y': 0.5}, duration=0.5)

        # Add cool pulsing animation to title
        anim2 = Animation(opacity=0.7, duration=0.7) + \
            Animation(opacity=1, duration=0.7)
        anim2.repeat = True

        # Start animations
        anim1.start(game_over_layout)
        Clock.schedule_once(lambda dt: anim2.start(game_over_title), 0.5)

        # Play game over sound effect if available
        # self.play_sound('game_over')

    def create_death_animation(self):
        """Create falling pieces animation when the snake dies"""
        snake_body = self.snake.body.copy()

        # Create container for debris
        self.death_debris_container = FloatLayout()
        self.game_over_container.add_widget(self.death_debris_container)

        # Schedule piece animations
        for i, segment in enumerate(snake_body):
            # Create a simple widget for each segment
            debris = Widget(
                size_hint=(None, None),
                size=(self.grid_size, self.grid_size),
                pos=(segment[0] * self.grid_size, segment[1] * self.grid_size)
            )

            # Add colored background to the widget
            with debris.canvas:
                # Get color from snake's color palette if available
                if hasattr(self.snake, 'segment_colors') and i < len(self.snake.segment_colors):
                    Color(*self.snake.segment_colors[i])
                else:
                    # Default snake color
                    Color(0, 0.7, 0, 1)
                Rectangle(pos=(0, 0), size=debris.size)

            self.death_debris_container.add_widget(debris)

            # Randomized falling animation - without rotation
            fall_speed = random.uniform(0.5, 1.5)
            dest_x = debris.x + random.uniform(-100, 100)
            # Add scale instead of rotation
            scale_to = random.uniform(0.2, 0.8)

            # Create falling animation - scale down as falling
            anim = Animation(
                pos=(dest_x, -50),
                size=(self.grid_size * scale_to, self.grid_size * scale_to),
                opacity=0,
                duration=fall_speed
            )

            # Start animation with slight delay based on segment position
            Clock.schedule_once(lambda dt, d=debris,
                                a=anim: a.start(d), i * 0.02)

    def reset_game(self):
        """Reset the game with smooth transitions"""
        # Play reset sound if available
        # self.play_sound('reset')

        # Add a flash effect
        flash = Rectangle(pos=(0, 0), size=(Window.width, Window.height))
        with self.canvas:
            Color(1, 1, 1, 0.3)
            flash_instruction = Rectangle(
                pos=(0, 0), size=(Window.width, Window.height))

        # Animate flash out
        def remove_flash(dt):
            self.canvas.remove(flash_instruction)

        Clock.schedule_once(remove_flash, 0.2)

        # Remove game over elements with animation
        if hasattr(self, 'game_over_container'):
            anim = Animation(opacity=0, duration=0.3)
            anim.bind(
                on_complete=lambda *args: self._complete_game_over_removal())
            anim.start(self.game_over_container)
        else:
            self._complete_game_reset()

        # Reset score tracking
        self.score = 0
        self.combo_counter = 0
        self.combo_multiplier = 1.0
        self.points_history = []

        if self.combo_timer:
            self.combo_timer.cancel()
            self.combo_timer = None

        # Update score label
        self.score_label.text = f"Score: {self.score} | High Score: {self.high_score}"
        self.combo_label.text = ""
        self.food_label.text = ""

    def _complete_game_over_removal(self):
        """Complete the removal of game over elements"""
        if hasattr(self, 'game_over_container'):
            self.remove_widget(self.game_over_container)
            delattr(self, 'game_over_container')

        if hasattr(self, 'game_over_bg'):
            self.canvas.remove(self.game_over_bg)
            delattr(self, 'game_over_bg')

        self._complete_game_reset()

    def _complete_game_reset(self):
        """Reset all game elements"""
        # Remove all widgets except permanent UI elements
        for child in self.children[:]:
            if child not in [self.score_label, self.food_label, self.level_label,
                             self.combo_label, self.score_history_widget]:
                self.remove_widget(child)

        # Reset pause state if needed
        if self.paused:
            self.paused = False
            if hasattr(self, 'pause_layout'):
                self.remove_widget(self.pause_layout)
                delattr(self, 'pause_layout')
            if hasattr(self, 'pause_bg'):
                self.canvas.remove(self.pause_bg)
                delattr(self, 'pause_bg')

        # Reset game state
        if hasattr(self.snake, 'tongue_animation') and self.snake.tongue_animation:
            self.snake.tongue_animation.cancel()

        if hasattr(self.food, 'cleanup'):
            self.food.cleanup()

        # Create new game objects with current grid settings
        self.snake = Snake(self.grid_size, self.grid_width, self.grid_height)
        self.food = Food(self.grid_size, self.grid_width, self.grid_height)
        self.obstacle = Obstacle(
            self.grid_size, self.grid_width, self.grid_height)

        # Apply difficulty setting to obstacles
        if hasattr(self, 'config') and 'difficulty' in self.config:
            self.obstacle.set_difficulty(self.config['difficulty'])

        # Generate initial obstacles
        self.obstacle.generate_obstacles(
            self.snake.body + [self.food.position])

        self.level = 1
        self.level_label.text = f"Level: {self.level}"
        self.game_over = False

        # Update positions of UI elements based on new grid size
        self.reposition_ui_elements()

    def reposition_ui_elements(self):
        """Reposition UI elements based on current grid size"""
        # Score label
        self.score_label.pos = (10, Window.height - 30)

        # Combo label
        self.combo_label.pos = (10, Window.height - 55)

        # Food info label
        self.food_label.pos = (10, Window.height - 80)

        # Level label
        self.level_label.pos = (Window.width - 100, Window.height - 30)

        # Score history visual
        self.score_history_widget.pos = (
            Window.width - 160, Window.height - 60)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    # Update keyboard handler for Q key (quit)
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]

        # Game controls
        if self.game_over:
            if key == 'r':
                self.reset_game()
                return True
            elif key == 'q':
                App.get_running_app().stop()
                return True

        if key == 'p':
            self.toggle_pause()
            return True

        if key == 'escape':  # ESC key can also toggle pause
            self.toggle_pause()
            return True

        if self.paused or self.game_over:
            return True

        # Movement controls
        if key == 'up':
            self.snake.change_direction((0, 1))
        elif key == 'down':
            self.snake.change_direction((0, -1))
        elif key == 'left':
            self.snake.change_direction((-1, 0))
        elif key == 'right':
            self.snake.change_direction((1, 0))

        return True

    def draw_grid(self):
        with self.canvas:
            # Draw background
            Color(0, 0, 0, 1)  # Black
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))

            # Draw grid lines (optional)
            Color(0.2, 0.2, 0.2, 1)  # Dark gray
            for i in range(self.grid_width + 1):
                Line(points=[i * self.grid_size, 0,
                     i * self.grid_size, Window.height])
            for i in range(self.grid_height + 1):
                Line(points=[0, i * self.grid_size,
                     Window.width, i * self.grid_size])

    def level_up(self):
        self.level += 1
        self.level_label.text = f"Level: {self.level}"

        # Create a level up notification
        level_up_label = Label(
            text=f"LEVEL {self.level}!",
            font_size='40sp',
            color=(1, 1, 0, 1),  # Yellow
            center_x=Window.width/2,
            center_y=Window.height/2
        )
        self.add_widget(level_up_label)

        # Animate the notification
        anim = Animation(opacity=0, duration=1.5)
        anim.bind(on_complete=lambda *args: self.remove_widget(level_up_label))
        anim.start(level_up_label)

        # Increase obstacle difficulty
        self.obstacle.increase_difficulty()

        # Generate new obstacles for the level
        occupied = self.snake.body + [self.food.position]
        self.obstacle.generate_obstacles(occupied)

        # Maybe speed up the game slightly?
        # You could implement this by adjusting the Clock.schedule_interval

    def toggle_pause(self):
        """Toggle the game's pause state with visual effects"""
        self.paused = not self.paused

        if self.paused:
            # Create pause overlay
            self.create_pause_overlay()
        else:
            # Remove pause overlay
            self.remove_pause_overlay()

    def create_pause_overlay(self):
        """Create a semi-transparent overlay with pause information"""
        # Create a semi-transparent background
        self.pause_bg = InstructionGroup()
        self.pause_bg.add(Color(0, 0, 0, 0.7))  # Semi-transparent black
        self.pause_bg.add(
            Rectangle(pos=(0, 0), size=(Window.width, Window.height)))
        self.canvas.add(self.pause_bg)

        # Create a vertical layout for pause menu
        self.pause_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(40)],
            size_hint=(0.4, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Pause title
        pause_title = Label(
            text="GAME PAUSED",
            font_size='40sp',
            color=(1, 1, 1, 1),
            size_hint=(1, 0.3),
            halign='center'
        )
        self.pause_layout.add_widget(pause_title)

        # Current score
        score_display = Label(
            text=f"Score: {self.score}",
            font_size='24sp',
            color=(0.9, 0.9, 0.5, 1),
            size_hint=(1, 0.2),
            halign='center'
        )
        self.pause_layout.add_widget(score_display)

        # Current level
        level_display = Label(
            text=f"Level: {self.level}",
            font_size='24sp',
            color=(0.7, 0.7, 1, 1),
            size_hint=(1, 0.2),
            halign='center'
        )
        self.pause_layout.add_widget(level_display)

        # Game controls info
        controls_info = Label(
            text="Controls:\nArrow keys - Move snake\nP - Resume game\nR - Restart (when game over)",
            font_size='18sp',
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, 0.4),
            halign='center',
            valign='middle'
        )
        self.pause_layout.add_widget(controls_info)

        # Resume button
        resume_button = Button(
            text="RESUME",
            font_size='20sp',
            size_hint=(0.8, 0.2),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.7, 0.2, 1)
        )
        resume_button.bind(on_press=lambda x: self.toggle_pause())
        self.pause_layout.add_widget(resume_button)

        # Add the layout to the game
        self.add_widget(self.pause_layout)

        # Animate the pause menu appearance
        self.pause_layout.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.pause_layout)

    def remove_pause_overlay(self):
        """Remove the pause overlay with animation"""
        if hasattr(self, 'pause_layout'):
            # Animate the pause menu disappearance
            anim = Animation(opacity=0, duration=0.2)
            anim.bind(on_complete=lambda *args: self._complete_pause_removal())
            anim.start(self.pause_layout)

    def _complete_pause_removal(self):
        """Complete the removal of pause elements after animation"""
        if hasattr(self, 'pause_layout'):
            self.remove_widget(self.pause_layout)
            delattr(self, 'pause_layout')

        if hasattr(self, 'pause_bg'):
            self.canvas.remove(self.pause_bg)
            delattr(self, 'pause_bg')

    def load_game_config(self):
        """Load or create default game configuration"""
        try:
            if self.config_store.exists('game_settings'):
                self.config = self.config_store.get('game_settings')
            else:
                # Default settings
                self.config = {
                    'grid_size': 20,
                    'game_speed': 10,
                    'difficulty': 'normal'
                }
                self.save_game_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            # Fallback defaults
            self.config = {
                'grid_size': 20,
                'game_speed': 10,
                'difficulty': 'normal'
            }

    def save_game_config(self):
        """Save current game configuration"""
        try:
            # Ensure data directory exists
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Save settings
            self.config_store.put('game_settings', **self.config)
        except Exception as e:
            print(f"Error saving config: {e}")

    def apply_game_settings(self):
        """Apply the current settings to the game"""
        # Unschedule current update
        if hasattr(self, 'update_event'):
            self.update_event.cancel()

        # Apply new grid size and recalculate grid dimensions
        self.grid_size = self.config['grid_size']
        self.grid_width = Window.width // self.grid_size
        self.grid_height = Window.height // self.grid_size

        # Apply new game speed
        self.game_speed = self.config['game_speed']
        self.update_event = Clock.schedule_interval(
            self.update, 1.0 / self.game_speed)

        # Rest of your apply settings code...

    def open_settings(self):
        """Open the settings overlay"""
        if self.paused or self.game_over:
            # Only allow settings when paused or game over
            self.create_settings_overlay()
        else:
            # Pause the game first
            self.toggle_pause()
            # Then open settings
            self.create_settings_overlay()

    def create_settings_overlay(self):
        """Create the settings menu overlay"""
        # Create a semi-transparent background
        self.settings_bg = InstructionGroup()
        self.settings_bg.add(Color(0, 0, 0, 0.8))  # Semi-transparent black
        self.settings_bg.add(
            Rectangle(pos=(0, 0), size=(Window.width, Window.height)))
        self.canvas.add(self.settings_bg)

        # Create main settings container
        self.settings_container = FloatLayout()

        # Create settings panel
        settings_panel = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint=(0.6, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=(0.15, 0.15, 0.15, 1)
        )

        # Add background color to panel
        with settings_panel.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            Rectangle(pos=settings_panel.pos, size=settings_panel.size)

        # Settings title
        settings_title = Label(
            text="GAME SETTINGS",
            font_size='36sp',
            color=(1, 1, 1, 1),
            size_hint=(1, 0.15)
        )
        settings_panel.add_widget(settings_title)

        # Grid Size setting
        grid_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        grid_label = Label(
            text="Grid Size:",
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(0.4, 1),
            halign='right',
            text_size=(None, None)
        )
        grid_layout.add_widget(grid_label)

        # Grid size options
        grid_options = BoxLayout(orientation='horizontal', size_hint=(0.6, 1))

        grid_sizes = [('Small', 30), ('Medium', 20), ('Large', 15)]
        for name, size in grid_sizes:
            btn = Button(
                text=name,
                font_size='18sp',
                background_color=(0.3, 0.3, 0.8, 1) if self.config['grid_size'] == size else (
                    0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=lambda x, s=size: self.set_grid_size(s))
            grid_options.add_widget(btn)

        grid_layout.add_widget(grid_options)
        settings_panel.add_widget(grid_layout)

        # Game Speed setting
        speed_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        speed_label = Label(
            text="Game Speed:",
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(0.4, 1),
            halign='right'
        )
        speed_layout.add_widget(speed_label)

        # Speed options
        speed_options = BoxLayout(orientation='horizontal', size_hint=(0.6, 1))

        # Updated speed settings
        speed_settings = [('Very Slow', 3), ('Slow', 5),
                          ('Normal', 7), ('Fast', 10), ('Insane', 15)]
        for name, speed in speed_settings:
            btn = Button(
                text=name,
                font_size='18sp',
                background_color=(0.3, 0.8, 0.3, 1) if self.config['game_speed'] == speed else (
                    0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=lambda x, s=speed: self.set_game_speed(s))
            speed_options.add_widget(btn)

        speed_layout.add_widget(speed_options)
        settings_panel.add_widget(speed_layout)

        # Difficulty setting
        diff_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        diff_label = Label(
            text="Difficulty:",
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(0.4, 1),
            halign='right'
        )
        diff_layout.add_widget(diff_label)

        # Difficulty options
        diff_options = BoxLayout(orientation='horizontal', size_hint=(0.6, 1))

        difficulties = ['easy', 'normal', 'hard', 'expert']
        for diff in difficulties:
            btn = Button(
                text=diff.capitalize(),
                font_size='18sp',
                background_color=(0.8, 0.3, 0.3, 1) if self.config['difficulty'] == diff else (
                    0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=lambda x, d=diff: self.set_difficulty(d))
            diff_options.add_widget(btn)

        diff_layout.add_widget(diff_options)
        settings_panel.add_widget(diff_layout)

        # Preview section
        preview_label = Label(
            text="Preview:",
            font_size='20sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, 0.1)
        )
        settings_panel.add_widget(preview_label)

        # Grid preview
        self.preview_widget = Widget(size_hint=(1, 0.15))
        settings_panel.add_widget(self.preview_widget)

        # Update the preview
        self.update_grid_preview()

        # Action buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5}
        )

        # Apply button
        apply_button = Button(
            text="APPLY",
            font_size='20sp',
            background_color=(0.2, 0.7, 0.2, 1),
            size_hint=(0.5, 1)
        )
        apply_button.bind(on_press=lambda x: self.apply_settings())
        button_layout.add_widget(apply_button)

        # Cancel button
        cancel_button = Button(
            text="CANCEL",
            font_size='20sp',
            background_color=(0.7, 0.2, 0.2, 1),
            size_hint=(0.5, 1)
        )
        cancel_button.bind(on_press=lambda x: self.close_settings())
        button_layout.add_widget(cancel_button)

        settings_panel.add_widget(button_layout)

        # Add settings panel to container
        self.settings_container.add_widget(settings_panel)

        # Add to game
        self.add_widget(self.settings_container)

        # Animate the settings panel appearance
        settings_panel.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(settings_panel)

    def update_grid_preview(self):
        """Update the grid size preview in settings"""
        self.preview_widget.canvas.clear()

        # Calculate preview dimensions
        preview_width = self.preview_widget.width
        preview_height = self.preview_widget.height

        # Calculate cell size based on current grid size setting
        cell_size = min(preview_width, preview_height) / 10

        # Calculate grid dimensions for preview
        preview_grid_width = int(preview_width / cell_size)
        preview_grid_height = int(preview_height / cell_size)

        # Draw preview grid
        with self.preview_widget.canvas:
            # Background
            Color(0, 0, 0, 1)
            Rectangle(pos=(0, 0), size=(preview_width, preview_height))

            # Grid lines
            Color(0.3, 0.3, 0.3, 1)
            for i in range(preview_grid_width + 1):
                Line(points=[i * cell_size, 0, i * cell_size, preview_height])
            for i in range(preview_grid_height + 1):
                Line(points=[0, i * cell_size, preview_width, i * cell_size])

            # Draw sample snake
            snake_x = preview_grid_width // 3
            snake_y = preview_grid_height // 2

            # Head
            Color(0, 0.9, 0, 1)
            Rectangle(
                pos=(snake_x * cell_size, snake_y * cell_size),
                size=(cell_size, cell_size)
            )

            # Body
            Color(0, 0.7, 0, 1)
            for i in range(1, 4):
                Rectangle(
                    pos=((snake_x - i) * cell_size, snake_y * cell_size),
                    size=(cell_size, cell_size)
                )

            # Food
            Color(1, 0, 0, 1)
            Rectangle(
                pos=((snake_x + 3) * cell_size, snake_y * cell_size),
                size=(cell_size, cell_size)
            )

    def set_grid_size(self, size):
        """Update the grid size setting"""
        self.config['grid_size'] = size
        # Update preview
        self.update_grid_preview()
        # Update button states
        for child in self.settings_container.children:
            if isinstance(child, BoxLayout):
                for layout in child.children:
                    if isinstance(layout, BoxLayout) and "Grid Size" in str(layout.children):
                        for options in layout.children:
                            if isinstance(options, BoxLayout):
                                for btn in options.children:
                                    if isinstance(btn, Button) and any(s[1] == size for s in [('Small', 30), ('Medium', 20), ('Large', 15)]):
                                        btn.background_color = (0.3, 0.3, 0.8, 1) if btn.text in [s[0] for s in [(
                                            'Small', 30), ('Medium', 20), ('Large', 15)] if s[1] == size] else (0.3, 0.3, 0.3, 1)

    def set_game_speed(self, speed):
        """Update the game speed setting"""
        self.config['game_speed'] = speed

        # Update button states in settings UI
        # ...existing code...

        # Preview the speed for the player
        preview_text = Label(
            text=f"Preview: {speed} FPS",
            font_size='16sp',
            color=(0.9, 0.9, 0.5, 1),
            center_x=Window.width/2,
            center_y=Window.height/2 - 100
        )
        self.settings_container.add_widget(preview_text)

        # Remove preview text after 1.5 seconds
        Clock.schedule_once(
            lambda dt: self.settings_container.remove_widget(preview_text), 1.5)

        # Update button states
        for child in self.settings_container.children:
            if isinstance(child, BoxLayout):
                for layout in child.children:
                    if isinstance(layout, BoxLayout) and "Game Speed" in str(layout.children):
                        for options in layout.children:
                            if isinstance(options, BoxLayout):
                                for btn in options.children:
                                    if isinstance(btn, Button) and any(s[1] == speed for s in [('Slow', 5), ('Normal', 10), ('Fast', 15), ('Insane', 20)]):
                                        btn.background_color = (0.3, 0.8, 0.3, 1) if btn.text in [s[0] for s in [(
                                            'Slow', 5), ('Normal', 10), ('Fast', 15), ('Insane', 20)] if s[1] == speed] else (0.3, 0.3, 0.3, 1)

    def set_difficulty(self, difficulty):
        """Update the difficulty setting"""
        self.config['difficulty'] = difficulty
        # Update button states
        for child in self.settings_container.children:
            if isinstance(child, BoxLayout):
                for layout in child.children:
                    if isinstance(layout, BoxLayout) and "Difficulty" in str(layout.children):
                        for options in layout.children:
                            if isinstance(options, BoxLayout):
                                for btn in options.children:
                                    if isinstance(btn, Button) and btn.text.lower() == difficulty:
                                        btn.background_color = (
                                            0.8, 0.3, 0.3, 1)
                                    elif isinstance(btn, Button):
                                        btn.background_color = (
                                            0.3, 0.3, 0.3, 1)

    def apply_settings(self):
        """Apply the settings and restart game"""
        # Save settings to config file
        self.save_game_config()

        # Close settings panel
        self.close_settings()

        # Apply the settings
        self.apply_game_settings()

        # Show confirmation
        config_applied = Label(
            text="Settings Applied!",
            font_size='24sp',
            color=(0.2, 1, 0.2, 1),
            center_x=Window.width/2,
            center_y=Window.height/2
        )
        self.add_widget(config_applied)

        # Animate confirmation
        anim = Animation(opacity=0, duration=1.5)
        anim.bind(on_complete=lambda *args: self.remove_widget(config_applied))
        anim.start(config_applied)

    def close_settings(self):
        """Close the settings overlay without saving"""
        # Reset config to saved values
        self.load_game_config()

        # Animate out and remove
        if hasattr(self, 'settings_container'):
            anim = Animation(opacity=0, duration=0.2)
            anim.bind(on_complete=lambda *args: self._complete_settings_removal())
            anim.start(self.settings_container)

    def _complete_settings_removal(self):
        """Complete removal of settings overlay"""
        if hasattr(self, 'settings_container'):
            self.remove_widget(self.settings_container)
            delattr(self, 'settings_container')

        if hasattr(self, 'settings_bg'):
            self.canvas.remove(self.settings_bg)
            delattr(self, 'settings_bg')


class SnakeGameApp(App):
    def build(self):
        return SnakeGame()


if __name__ == '__main__':
    SnakeGameApp().run()
