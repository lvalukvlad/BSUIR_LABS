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
    width = abs(x1 - x0)
    height = abs(y1 - y0)
    a = max(width // 4, 2)
    b = max(height // 4, 2)
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    points = []

    x = a
    while x <= width // 2:
        y_squared = (x * x) / (a * a) - 1
        if y_squared >= 0:
            y = int(b * math.sqrt(y_squared))

            if y > 0:
                points.append(Pixel(Point(cx + x, cy + y)))
                points.append(Pixel(Point(cx + x, cy - y)))
                points.append(Pixel(Point(cx - x, cy + y)))
                points.append(Pixel(Point(cx - x, cy - y)))
        x += 1

    y = b
    while y <= height // 2:
        x_squared = 1 + (y * y) / (b * b)
        x = int(a * math.sqrt(x_squared))

        if x <= width // 2:
            points.append(Pixel(Point(cx + x, cy + y)))
            points.append(Pixel(Point(cx + x, cy - y)))
            points.append(Pixel(Point(cx - x, cy + y)))
            points.append(Pixel(Point(cx - x, cy - y)))
        y += 1

    return points

name = "Гипербола"