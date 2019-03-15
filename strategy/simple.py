from model.functions import snake_would_collide_with_wall, snake_would_collide_with_snake, snake_could_die_head_to_head, \
    snake_could_die_in_death_end, calc_path, snake_could_kill_head_to_head, get_move_from_pos

OPTIONS = ['up', 'down', 'left', 'right']


def apply_rating(options, keys, modificator):
    for key in keys:
        try:
            options[key] = options[key] + modificator
        except:
            print("unable to handle key")




def calulate(board, snake_id):
    #
    #   Negative Points
    #

    options = list(filter(lambda move: not snake_would_collide_with_wall(board, snake_id)(move), OPTIONS))
    options = list(filter(lambda move: not snake_would_collide_with_snake(board, snake_id)(move), options))

    rated_moves = {move: 0 for move in options}

    apply_rating(
        rated_moves,
        filter(snake_could_die_head_to_head(board, snake_id), options),
        -500
    )

    apply_rating(
        rated_moves,
        filter(snake_could_die_in_death_end(board, snake_id), options),
        -800
    )

    #
    #   Positive Points
    #
    #   1. Eat if hungry
    #   2. Kill if possible
    #   3. Follow Tail
    #

    paths_to_food = sorted([calc_path(board, board.snakes[snake_id].head, food) for food in board.food],
                           key=lambda path: len(path))

    if len(paths_to_food):
        nearest_food_path = paths_to_food[0]

        if len(nearest_food_path) >= board.snakes[snake_id].health:
            food_ratio = 100
        elif board.snakes[snake_id].health < 50:
            food_ratio = 100 - board.snakes[snake_id].health
        else:
            food_ratio = 0
    else:
        nearest_food = []
        food_ratio = 0

    apply_rating(
        rated_moves,
        [get_move_from_pos(board.snakes[snake_id].head, nearest_food_path[0])],
        food_ratio
    )

    apply_rating(
        rated_moves,
        filter(snake_could_kill_head_to_head(board, snake_id), options),
        50
    )

    return rated_moves