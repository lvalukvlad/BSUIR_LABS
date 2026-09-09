from dataclasses import dataclass
from algorithms.lab_3.matrix import get_curve_matrix, multiply_vector

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass
class Pixel:
    point: Point
    intensity: float = 1.0

def generate(points, num_steps=100):
    if len(points) != 4:
        raise ValueError("Кривая Безье требует ровно 4 контрольные точки")
    M = get_curve_matrix("Безье")
    for i in range(num_steps + 1):
        t = i / num_steps
        t3 = t * t * t
        t2 = t * t
        T = [t3, t2, t, 1]
        coeffs = multiply_vector(M, T)
        x = coeffs[0] * points[0].x + coeffs[1] * points[1].x + coeffs[2] * points[2].x + coeffs[3] * points[3].x
        y = coeffs[0] * points[0].y + coeffs[1] * points[1].y + coeffs[2] * points[2].y + coeffs[3] * points[3].y
        yield Pixel(Point(int(round(x)), int(round(y))))
name = "Безье"



