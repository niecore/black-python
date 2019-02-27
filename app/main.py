import json
import os
import random
import bottle
import numpy as np

from app.api import ping_response, start_response, move_response, end_response

OPTIONS = ['up', 'down', 'left', 'right']


@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = ["#000000"]

    return start_response(random.choice)


def get_snake_head(snake):
    return snake["body"][0]


def get_new_position(pos, move):
    new_pos = pos.copy()

    if move == "up":
        new_pos["y"] = new_pos["y"] - 1
    elif move == "down":
        new_pos["y"] = new_pos["y"] + 1
    elif move == "left":
        new_pos["x"] = new_pos["x"] - 1
    elif move == "right":
        new_pos["x"] = new_pos["x"] + 1
    else:
        pass

    return new_pos


def get_snake_len(snake):
    return len(snake["body"])


def is_first_iteration(data):
    return all(x == data["you"]["body"][0] for x in data["you"]["body"])


def get_previous_snake_moves(snake):
    prev = get_snake_head(snake)
    moves = []
    for position in snake["body"][1:]:
        for move in OPTIONS:
            if collide(get_new_position(position, move), prev):
                moves.append(move)

        prev = position

    return moves


def collide(a, b):
    return a["x"] == b["x"] and a["y"] == b["y"]


def will_collide_wall(snake, height, width):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)
        return not (width > next_head["x"] >= 0 and height > next_head["y"] >= 0)

    return f


def will_collide_snake(snake, snakes):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)

        for other_snake in snakes:
            for position in other_snake["body"][:-1]:
                if collide(position, next_head):
                    return True

        return False

    return f


def will_collide_head_to_head(snake, snakes):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)

        for other_snake in get_other_snakes(snake, snakes):
            for other_move in OPTIONS:
                if collide(next_head, get_new_position(get_snake_head(other_snake), other_move)) \
                        and get_snake_len(other_snake) >= get_snake_len(snake):
                    return True

        return False

    return f


def will_kill_head_to_head(snake, snakes):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)

        for other_snake in get_other_snakes(snake, snakes):
            for other_move in OPTIONS:
                if collide(next_head, get_new_position(get_snake_head(other_snake), other_move)) \
                        and get_snake_len(other_snake) < get_snake_len(snake):
                    return True

        return False

    return f


def get_other_snakes(snake, snakes):
    return list(
        filter(
            lambda other_snake: other_snake["id"] != snake["id"],
            snakes
        )
    )


def distance_from_snake(snake):
    def f(food):
        food["distance"] = abs(food["x"] - get_snake_head(snake)["x"]) + abs(food["y"] - get_snake_head(snake)["y"])
        return food

    return f


def calculate_path(snake, food, strategy="squared"):
    moves = []

    if strategy == "squared":

        if food["x"] > get_snake_head(snake)["x"]:
            moves.append("right")
        elif food["x"] < get_snake_head(snake)["x"]:
            moves.append("left")

        if food["y"] > get_snake_head(snake)["y"]:
            moves.append("down")
        elif food["y"] < get_snake_head(snake)["y"]:
            moves.append("up")

    else:
        pass

    return moves


def reachable_positions_after_move(matrix, snake_head, move):
    pos = get_new_position(snake_head, move)
    _matrix = np.copy(matrix)
    floodfill(_matrix, pos["y"], pos["x"])
    return np.count_nonzero(_matrix == -1)


def floodfill(matrix, x, y):
    if matrix[x][y] == 0:
        matrix[x][y] = -1
        # recursively invoke flood fill on all surrounding cells:
        if x > 0:
            floodfill(matrix, x - 1, y)
        if x < len(matrix[y]) - 1:
            floodfill(matrix, x + 1, y)
        if y > 0:
            floodfill(matrix, x, y - 1)
        if y < len(matrix) - 1:
            floodfill(matrix, x, y + 1)
    else:
        return


def apply_rating(options, keys, modificator):

    for key in keys:
        try:
            options[key] = options[key] + modificator
        except:
            print("unable to handle key")


def get_snake_matrix(snake0, snakes, width, height):
    matrix = np.zeros((width, height))

    SNAKE_N = 1
    SNAKE_N_HEAD = 2
    SNAKE_0 = 3
    SNAKE_0_HEAD = 4
    FOOD = 5

    for snake in snakes:
        head = snake["body"][0]
        matrix[head["y"]][head["x"]] = SNAKE_N_HEAD
        for pos in snake["body"][1:-1]:
            matrix[pos["y"]][pos["x"]] = SNAKE_N

    head = snake0["body"][0]
    matrix[head["y"]][head["x"]] = SNAKE_0_HEAD
    for pos in snake0["body"][1:-1]:
        matrix[pos["y"]][pos["x"]] = SNAKE_0

    return matrix


def calculate_best_move(snake0, snakes, height, width, food):

    rated_options = {option: 0 for option in OPTIONS}
    #
    #   Negative Points
    #

    # wall collusion
    wall_collusions = list(filter(will_collide_wall(snake0, height, width), OPTIONS))
    options = list(set(OPTIONS) - set(wall_collusions))

    # snake collusion
    snake_collusions = list(filter(will_collide_snake(snake0, snakes), options))

    # dead end
    dead_ends = filter(
        lambda move: reachable_positions_after_move(matrix, get_snake_head(snake0), move) <= get_snake_len(snake0),
        options)

    # head to head deaths
    head_to_head_deaths = list(filter(will_collide_head_to_head(snake0, snakes), options))

    apply_rating(rated_options, wall_collusions, -1000)
    apply_rating(rated_options, snake_collusions, -1000)
    apply_rating(rated_options, dead_ends, -800)
    apply_rating(rated_options, head_to_head_deaths, -500)

    #
    #   Positive Points
    #
    #   1. Eat if hungry
    #   2. Kill if possible
    #   3. Continue moving
    #

    # food moves
    nearest_food = sorted(list(map(distance_from_snake(snake0), food)), key=lambda x: x["distance"])[0]
    nearest_food_routes = calculate_path(snake0, nearest_food)

    if nearest_food["distance"] >= snake0["health"]:
        food_ratio = 100
    elif snake0["health"] < 50:
        food_ratio = 100 - snake["health"]
    else:
        food_ratio = 0

    # head to head kills
    # Notes: head to head kills might unlock dead ends
    possible_head_to_head_kills = list(filter(will_kill_head_to_head(snake0, snakes), options))

    # keep moving
    previous_move = get_previous_snake_moves(data["you"])
    if len(previous_move) != 0:
        previous_move = previous_move[0:1]

    apply_rating(rated_options, nearest_food_routes, food_ratio)
    apply_rating(rated_options, possible_head_to_head_kills, 50)
    apply_rating(rated_options, previous_move, 10)

    return rated_options


@bottle.post('/move')
def move():

    # Todo:
    #
    # 1. Utilize space when in dead end
    #
    #
    #
    #

    data = bottle.request.json
    print(json.dumps(data))

    snake0 = data["you"]
    snakes = data["board"]["snakes"]
    height = data["board"]["height"]
    width = data["board"]["width"]
    food = data["board"]["food"]

    matrix = get_snake_matrix(snake0, snakes, width, height)

    for snake0 in snakes:
        move_options = calculate_best_move(snake0, snakes, height, width, food)




    return move_response(max(rated_options, key=rated_options.get))


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
