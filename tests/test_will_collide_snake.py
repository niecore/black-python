from unittest import TestCase

from app.main import will_not_collide_wall


class TestWill_collide_snake(TestCase):
    def test_will_collide_snake(self):
        snake = {
            "body": [
                {"x": 1, "y": 1},
                {"x": 1, "y": 1},
                {"x": 1, "y": 1},
            ]
        }
        assert True == will_not_collide_wall(snake, 3, 3)("up")
        assert True == will_not_collide_wall(snake, 3, 3)("down")
        assert True == will_not_collide_wall(snake, 3, 3)("left")
        assert True == will_not_collide_wall(snake, 3, 3)("right")

    def test_will_collide_snake2(self):
        snake = {
            "body": [
                {"x": 0, "y": 0},
                {"x": 0, "y": 0},
                {"x": 0, "y": 0},
            ]
        }

        assert False == will_not_collide_wall(snake, 1, 1)("up")
        assert False == will_not_collide_wall(snake, 1, 1)("down")
        assert False == will_not_collide_wall(snake, 1, 1)("left")
        assert False == will_not_collide_wall(snake, 1, 1)("right")

    def test_will_collide_snake2(self):
        snake = {"body": [{"x": 10, "y": 0}, {"x": 11, "y": 0}, {"x": 11, "y": 1}]}
        assert False == will_not_collide_wall(snake, 15, 15)("down")
        assert True == will_not_collide_wall(snake, 15, 15)("up")