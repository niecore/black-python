import json
import os

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

    color = "#000000"

    return start_response(color)


def get_snake_head(snake):
    return snake["body"][0]


def get_snake_tail(snake):
    return snake["body"][:-1]


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


def wall_collusion(pos, height, width):
    return not (width > pos["x"] >= 0 and height > pos["y"] >= 0)


def will_collide_wall(snake, height, width):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)
        return wall_collusion(next_head, height, width)

    return f


def snake_collusion(pos, snakes):
    for other_snake in snakes:
        for position in other_snake["body"][:-1]:
            if collide(position, pos):
                return True

    return False


def will_collide_snake(snake, snakes):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)
        return snake_collusion(next_head, snakes)

    return f


def starved(snake0):
    return snake0["health"] == 0


def head_to_head_death(snake0, snakes):
    for other_snake in get_other_snakes(snake0, snakes):
        if collide(get_snake_head(snake0), get_snake_head(other_snake)) \
                and get_snake_len(other_snake) >= get_snake_len(snake):
            return True
    return False


def could_collide_head_to_head(snake, snakes):
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
    matrix = get_snake_matrix(snake0, snakes, width, height)
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
    head_to_head_deaths = list(filter(could_collide_head_to_head(snake0, snakes), options))

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
    nearest_foods = sorted(list(map(distance_from_snake(snake0), food)), key=lambda x: x["distance"])

    if len(nearest_foods):
        nearest_food = nearest_foods[0]
        nearest_food_routes = calculate_path(snake0, nearest_food)

        if nearest_food["distance"] >= snake0["health"]:
            food_ratio = 100
        elif snake0["health"] < 50:
            food_ratio = 100 - snake0["health"]
        else:
            food_ratio = 0
    else:
        nearest_food_routes = []
        food_ratio = 0

    # head to head kills
    # Notes: head to head kills might unlock dead ends
    possible_head_to_head_kills = list(filter(will_kill_head_to_head(snake0, snakes), options))

    # keep moving
    previous_move = get_previous_snake_moves(snake0)
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
    # 2. Block ways of other snakes
    #

    data = bottle.request.json
    print(json.dumps(data))

    snake0 = data["you"]
    snakes = data["board"]["snakes"]
    height = data["board"]["height"]
    width = data["board"]["width"]
    foods = data["board"]["food"]

    for snake0 in snakes:
        snake0.update({"alive": True})

    snakes_alive = filter(lambda snake0: snake0["alive"] is True, snakes)

    move_options = [calculate_best_move(snake0, snakes, height, width, foods) for snake0 in snakes_alive]

    # Move head by adding a new body part at the start of the body array in the move direction
    for rated_options, snake0 in zip(move_options, snakes_alive):
        fav_move = max(rated_options, key=rated_options.get)
        snake0["body"].insert(0, get_new_position(get_snake_head(snake0), fav_move))

    # Reduce health
    for snake0 in snakes_alive:
        snake0["health"] = snake0["health"] - 1

    # Check if the snake ate and adjust health
    # If the snake ate this turn, add a new body segment, underneath the current tail.
    # Remove eaten food
    for snake0 in snakes_alive:
        if get_snake_head(snake0) in foods:
            snake0["health"] = 100
            snake0["body"].append = snake0["body"][:-1]
            foods = filter(lambda food: food == get_snake_head(snake0), foods)

    # Remove the final body segment
    for snake0 in snakes_alive:
        del snake0["body"][-1]

    # Check for snake death
    for snake0 in snakes_alive:
        if wall_collusion(get_snake_head(snake0), height, width) or \
                snake_collusion(get_snake_head(snake0), snakes_alive) or \
                starved(snake0) or \
                head_to_head_death(snake0, snakes_alive):
            snake0["alive"] = False

    # fall back
    meh = calculate_best_move(snake0, snakes, height, width, foods)
    return move_response(max(meh, key=meh.get))


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
