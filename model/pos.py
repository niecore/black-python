from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Point:
    x: int
    y: int

    def move(self, move):
        new_pos = Point(self.x, self.y)

        if move == "up":
            new_pos.y = new_pos.y - 1
        elif move == "down":
            new_pos.y = new_pos.y + 1
        elif move == "left":
            new_pos.x = new_pos.x - 1
        elif move == "right":
            new_pos.x = new_pos.x + 1
        else:
            pass

        return new_pos


