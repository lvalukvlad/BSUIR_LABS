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
    steps = max(abs(dx), abs(dy))

    if steps == 0:
        yield Pixel(Point(x0, y0))
        return

    x_inc = dx / steps
    y_inc = dy / steps
    x, y = float(x0), float(y0)

    for _ in range(steps + 1):
        yield Pixel(Point(round(x), round(y)))
        x += x_inc
        y += y_inc


name = "ЦДА"