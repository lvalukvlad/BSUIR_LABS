from dataclasses import dataclass
from algorithms.lab_3.matrix import get_curve_matrix

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass
class Pixel:
    point: Point
    intensity: float = 1.0

def generate(points, num_steps=100):
    if len(points) < 4:
        raise ValueError("B-сплайн требует минимум 4 точки")
    for seg in range(len(points) - 3):
        for step in range(num_steps + 1):
            t = step / num_steps
            b0 = (1 - t) ** 3 / 6
            b1 = (3 * t ** 3 - 6 * t ** 2 + 4) / 6
            b2 = (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) / 6
            b3 = t ** 3 / 6
            p0, p1, p2, p3 = points[seg:seg+4]
            x = b0 * p0.x + b1 * p1.x + b2 * p2.x + b3 * p3.x
            y = b0 * p0.y + b1 * p1.y + b2 * p2.y + b3 * p3.y
            yield Pixel(Point(int(round(x)), int(round(y))))

name = "B-сплайн"

