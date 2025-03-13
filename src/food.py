class Food:
    def __init__(self, board_size):
        self.board_size = board_size
        self.position = self.spawn_food()

    def spawn_food(self):
        import random
        x = random.randint(0, self.board_size[0] - 1)
        y = random.randint(0, self.board_size[1] - 1)
        return (x, y)

    def check_eaten(self, snake_position):
        return self.position == snake_position