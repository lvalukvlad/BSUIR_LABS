
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass
class Pixel:
    point: Point
    intensity: float = 1.0


def generate(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0

    if abs(dx) >= abs(dy):
        limit = abs(dx)
        p = limit / 10.0
        direction = 1 if dx > 0 else -1

        for t in range(int(limit) + 1):
            x = t
            y_sq = 2 * p * t
            if y_sq < 0:
                break
            y = int(math.sqrt(y_sq))

            yield Pixel(Point(x0 + direction * x, y0 + y))
            if y != 0:
                yield Pixel(Point(x0 + direction * x, y0 - y))
    else:
        limit = abs(dy)
        p = limit / 10.0
        direction = 1 if dy > 0 else -1

        for t in range(limit + 1):
            y = t
            x_sq = 2 * p * t
            if x_sq < 0:
                break
            x = int(math.sqrt(x_sq))

            yield Pixel(Point(x0 + x, y0 + direction * y))
            if x != 0:
                yield Pixel(Point(x0 - x, y0 + direction * y))


name = "Парабола"