import json
import os
import random
import bottle

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

    color = "#00FF00"

    return start_response(color)


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


def will_not_collide_wall(snake, height, width):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)
        return width > next_head["x"] >= 0 and height > next_head["y"] >= 0

    return f


def will_not_collide_snake(snake, snakes):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)

        for other_snake in snakes:
            for position in other_snake["body"]:
                if collide(position, next_head):
                    return False

        return True

    return f


def get_other_snakes(snake, snakes):
    return list(
        filter(
            lambda other_snake: other_snake["id"] != snake["id"],
            snakes
        )
    )


def will_not_collide_head_to_head(snake, snakes):
    def f(move):
        next_head = get_new_position(get_snake_head(snake), move)

        for other_snake in get_other_snakes(snake, snakes):
            for other_move in OPTIONS:
                if collide(next_head, get_new_position(get_snake_head(other_snake), other_move)):
                    return False

        return True

    return f


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
        else:
            moves.append(None)

        if food["y"] > get_snake_head(snake)["y"]:
            moves.append("down")
        elif food["y"] < get_snake_head(snake)["y"]:
            moves.append("up")
        else:
            moves.append(None)
    else:
        pass

    return moves

@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    previous_moves = get_previous_snake_moves(data["you"])

    options = OPTIONS
    options = list(filter(will_not_collide_wall(data["you"], data["board"]["height"], data["board"]["width"]), options))
    options = list(filter(will_not_collide_snake(data["you"], data["board"]["snakes"]), options))
    options = list(filter(will_not_collide_head_to_head(data["you"], data["board"]["snakes"]), options))


    if data["you"]["health"] < 50:
        nearest_food = sorted(list(map(distance_from_snake(data["you"]), data["board"]["food"])), key=lambda x: x["distance"])[0]
        path_to_food = calculate_path(data["you"], nearest_food)
    else:
        path_to_food = [None, None]

    if path_to_food[0] in options:
        the_move = path_to_food[0]
    elif path_to_food[1] in options:
        the_move = path_to_food[1]
    elif len(previous_moves) != 0 and previous_moves[0] in options:
        the_move = previous_moves[0]
    else:
        the_move = random.choice(options)

    print(f"Available moves: {options} Chosen move: {the_move}")
    print(f"Previous moves: {previous_moves}")
    print(f"Path to nearest food: {path_to_food}")

    return move_response(the_move)


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
