# Author: Christian Careaga (christian.careaga7@gmail.com)
# A* Pathfinding in Python (2.7)
# Please give credit if used
from heapq import *

import numpy as np


def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


def astar(array, start, goal):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    array[goal[0]][goal[1]] = 0

    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []

    heappush(oheap, (fscore[start], start))

    while oheap:

        current = heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[neighbor[0]][neighbor[1]] != 0:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))

    return False


# import json
#
# def get_snake_matrix(snake0, snakes, width, height):
#     matrix = np.zeros((width, height))
#
#     SNAKE_N = 1
#     SNAKE_N_HEAD = 2
#     SNAKE_0 = 3
#     SNAKE_0_HEAD = 4
#     FOOD = 5
#
#     for snake in snakes:
#         head = snake["body"][0]
#         matrix[head["y"]][head["x"]] = SNAKE_N_HEAD
#         for pos in snake["body"][1:-1]:
#             matrix[pos["y"]][pos["x"]] = SNAKE_N
#
#     head = snake0["body"][0]
#     matrix[head["y"]][head["x"]] = SNAKE_0_HEAD
#     for pos in snake0["body"][1:-1]:
#         matrix[pos["y"]][pos["x"]] = SNAKE_0
#
#     return matrix
#
#
# data = json.loads(
#     '{"game": {"id": "c170cc39-76a3-40b1-a876-18cb5c5f6521"}, "turn": 14, "board": {"height": 11, "width": 11, "food": [{"x": 8, "y": 7}, {"x": 9, "y": 7}, {"x": 9, "y": 6}, {"x": 0, "y": 6}, {"x": 5, "y": 7}, {"x": 3, "y": 2}], "snakes": [{"id": "gs_qrhqFHbM7fdJCbcxyVDMhDdS", "name": "matthewlehner / The Undersnaker", "health": 89, "body": [{"x": 1, "y": 7}, {"x": 1, "y": 8}, {"x": 1, "y": 9}, {"x": 0, "y": 9}]}, {"id": "gs_PyrtpMQf6tKS7kVp6BxQgWy4", "name": "LayCraft / Heel Bruiser", "health": 98, "body": [{"x": 3, "y": 9}, {"x": 4, "y": 9}, {"x": 5, "y": 9}, {"x": 5, "y": 10}]}, {"id": "gs_j3YtXrGyCjJGvK9rdWmKbfWS", "name": "Petah / Rando", "health": 92, "body": [{"x": 1, "y": 1}, {"x": 2, "y": 1}, {"x": 2, "y": 2}, {"x": 2, "y": 3}]}, {"id": "gs_BMwgcMqMf3FyhBdxTxRRFTFM", "name": "niecore / black-python", "health": 93, "body": [{"x": 0, "y": 4}, {"x": 0, "y": 3}, {"x": 0, "y": 2}, {"x": 0, "y": 1}]}, {"id": "gs_gmcTJFvhJ97CBYtRKjD9DrH8", "name": "SamWheating / Oracow", "health": 86, "body": [{"x": 3, "y": 7}, {"x": 3, "y": 8}, {"x": 2, "y": 8}]}, {"id": "gs_JFBKMSbCg4cvPCRJxmrhKWVW", "name": "JerryKott / Krakenator", "health": 86, "body": [{"x": 8, "y": 6}, {"x": 7, "y": 6}, {"x": 7, "y": 5}]}, {"id": "gs_GyF4H644crPcTbFXt7SDmWXB", "name": "lduchosal / markdavid-0.6", "health": 91, "body": [{"x": 4, "y": 6}, {"x": 4, "y": 5}, {"x": 4, "y": 4}, {"x": 4, "y": 3}]}]}, "you": {"id": "gs_BMwgcMqMf3FyhBdxTxRRFTFM", "name": "niecore / black-python", "health": 93, "body": [{"x": 0, "y": 4}, {"x": 0, "y": 3}, {"x": 0, "y": 2}, {"x": 0, "y": 1}]}}')
#
# data = json.loads(
#     '{"game": {"id": "c0a1c1c5-555d-4d24-86ab-5179ead7cd99"}, "turn": 546, "board": {"height": 15, "width": 15, "food": [{"x": 10, "y": 0}, {"x": 6, "y": 14}, {"x": 12, "y": 14}, {"x": 14, "y": 3}, {"x": 6, "y": 2}, {"x": 14, "y": 12}, {"x": 5, "y": 0}, {"x": 11, "y": 14}, {"x": 9, "y": 3}, {"x": 6, "y": 0}], "snakes": [{"id": "b019a918-9113-4561-9f72-ca512c6d2480", "name": "a", "health": 100, "body": [{"x": 7, "y": 14}, {"x": 7, "y": 13}, {"x": 7, "y": 12}, {"x": 7, "y": 11}, {"x": 7, "y": 10}, {"x": 7, "y": 9}, {"x": 7, "y": 8}, {"x": 8, "y": 8}, {"x": 9, "y": 8}, {"x": 10, "y": 8}, {"x": 11, "y": 8}, {"x": 12, "y": 8}, {"x": 13, "y": 8}, {"x": 14, "y": 8}, {"x": 14, "y": 9}, {"x": 14, "y": 9}]}]}, "you": {"id": "b019a918-9113-4561-9f72-ca512c6d2480", "name": "a", "health": 100, "body": [{"x": 7, "y": 14}, {"x": 7, "y": 13}, {"x": 7, "y": 12}, {"x": 7, "y": 11}, {"x": 7, "y": 10}, {"x": 7, "y": 9}, {"x": 7, "y": 8}, {"x": 8, "y": 8}, {"x": 9, "y": 8}, {"x": 10, "y": 8}, {"x": 11, "y": 8}, {"x": 12, "y": 8}, {"x": 13, "y": 8}, {"x": 14, "y": 8}, {"x": 14, "y": 9}, {"x": 14, "y": 9}]}}'
# )
#
# matrix = get_snake_matrix(data["you"], data["board"]["snakes"], data["board"]["width"], data["board"]["height"])
# print(matrix)
# print(astar(matrix, (14, 9), (7, 14)))
