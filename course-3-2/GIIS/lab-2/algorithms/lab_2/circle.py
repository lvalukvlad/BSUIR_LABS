from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass
class Pixel:
    point: Point
    intensity: float = 1.0


def generate(cx, cy, r):
    x = 0
    y = r
    d = 3 - 2 * r

    while x <= y:
        yield Pixel(Point(cx + x, cy + y))
        yield Pixel(Point(cx - x, cy + y))
        yield Pixel(Point(cx + x, cy - y))
        yield Pixel(Point(cx - x, cy - y))
        yield Pixel(Point(cx + y, cy + x))
        yield Pixel(Point(cx - y, cy + x))
        yield Pixel(Point(cx + y, cy - x))
        yield Pixel(Point(cx - y, cy - x))

        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y = y - 1
        x = x + 1


name = "Окружность"


