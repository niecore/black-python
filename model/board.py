import numpy as np

from model.pos import Point
from model.snake import Snake


class Board:
    MATRIX_SNAKE_HEAD_0 = 100
    MATRIX_SNAKE_HEAD_N = 200
    MATRIX_FOOD = -1
    MATRIX_EMPTY = 0

    def __init__(self, snakes, food, width, height):
        self.snakes = snakes
        self.food = food
        self.width = width
        self.height = height

        self.matrix = self._create_matrix()

    def _create_matrix(self):

        matrix = np.zeros((self.width, self.height))

        for i, snake in enumerate(self.snakes.values()):
            for pos in snake.body:
                matrix[pos.x][pos.y] = i + 1

            matrix[snake.head.y][snake.head.x] = self.MATRIX_SNAKE_HEAD_N

        return matrix

    @classmethod
    def from_dict(cls, board_dict):
        return cls(
            {snake["id"]: Snake.from_dict(snake) for snake in board_dict["snakes"]},
            [Point(food["x"], food["y"]) for food in board_dict["food"]],
            board_dict["width"],
            board_dict["height"]
        )

    def get_field(self, pos):
        return self.matrix[pos.x][pos.y]
