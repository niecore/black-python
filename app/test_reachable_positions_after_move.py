from unittest import TestCase

import numpy as np

from app.main import reachable_positions_after_move


class TestReachable_positions_after_move(TestCase):
    def test_reachable_positions_after_move(self):

        ar = np.zeros((4, 4))

        ar[0][1] = 1
        ar[1][1] = 1
        ar[2][1] = 1
        ar[3][1] = 1

        snake = {
            "body": [
                {"x": 0, "y": 1},
                {"x": 1, "y": 1},
                {"x": 2, "y": 1},
                {"x": 3, "y": 1},
            ]
        }

        assert 4 == reachable_positions_after_move(ar, {"x": 1, "y": 0}, "left")

    def test_reachable_positions_after_move2(self):

        ar = np.zeros((4, 4))

        ar[0][1] = 1
        ar[1][1] = 1
        ar[2][1] = 1
        ar[3][1] = 1

        snake = {
            "body": [
                {"x": 0, "y": 1},
                {"x": 1, "y": 1},
                {"x": 2, "y": 1},
                {"x": 3, "y": 1},
            ]
        }

        assert 8 == reachable_positions_after_move(ar, {"x": 1, "y": 0}, "right")