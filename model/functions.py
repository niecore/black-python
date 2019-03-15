import numpy as np

from strategy.a_star import astar
from strategy.flood_fill import floodfill


def distance(a, b):
    return abs(a.x - a.x) + abs(a.y - b.y)


def get_move_from_pos(a, b):
    if distance(a, b) != 1:
        return None

    for move in ['up', 'down', 'left', 'right']:
        if a.move(move) == b:
            return move


def wall_collusion(pos, width, height):
    return not (width > pos.x >= 0 and height > pos.y >= 0)


def snake_collusion(pos, board):
    return board.get_field(pos) > 0


def head_collusion_possible(pos, board, snake_id):
    return distance(pos, board.snakes[snake_id].head) == 1


def snake_would_collide_with_wall(board, snake_id):
    return lambda move: wall_collusion(board.snakes[snake_id].head.move(move), board.width, board.height)


def snake_would_collide_with_snake(board, snake_id):
    return lambda move: snake_collusion(board.snakes[snake_id].head.move(move), board)


def stronger_snakes(board, snake_id):
    return filter(lambda x: len(x) >= len(board.snakes[snake_id]), board.snakes)


def other_snakes(board, snake_id):
    return filter(lambda x: x.id != snake_id, board.snakes)


def weaker_snakes(board, snake_id):
    return filter(lambda x: len(x) < len(board.snakes[snake_id]), board.snakes)


def snake_could_die_head_to_head(board, snake_id):
    return lambda move: (
            True in
            [
                head_collusion_possible(board.snakes[snake_id].head.move(move), board, other_snake)
                for other_snake in stronger_snakes(board, snake_id)
            ]
    )


def snake_could_kill_head_to_head(board, snake_id):
    return lambda move: (
            True in
            [
                head_collusion_possible(board.snakes[snake_id].head.move(move), board, other_snake)
                for other_snake in weaker_snakes(board, snake_id)
            ]
    )


def reachable_positions(pos, board):
    _matrix = np.copy(board.matrix)
    floodfill(_matrix, pos)
    return np.count_nonzero(_matrix == -100)


def snake_could_die_in_death_end(board, snake_id):
    return lambda move: (
            reachable_positions(board.snakes[snake_id].head.move(move), board) < len(board.snakes[snake_id])
    )


def calc_path(board, start, goal):
    return astar(board.matrix, start, goal)
