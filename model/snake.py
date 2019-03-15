from dataclasses import dataclass, field
from typing import List

from model.pos import Point

@dataclass
class Snake:
    id: str
    health: int
    body: List[Point]
    head: Point = field(init=False)

    def __post_init__(self):
        self.head = self.body[0]
        self.body = self.body[1:]

    def __len__(self):
        return len(self.body) + 1

    @classmethod
    def from_dict(cls, snake_dict):
        return cls(
            snake_dict["id"],
            snake_dict["health"],
            [Point(body["x"], body["y"]) for body in snake_dict["body"]],
        )