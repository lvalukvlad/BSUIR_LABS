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
        raise ValueError("Кривая Эрмита требует ровно 4 точки: P0, T0, T1, P1")
    M = get_curve_matrix("Эрмит")
    for i in range(num_steps + 1):
        t = i / num_steps
        t3 = t * t * t
        t2 = t * t
        T = [t3, t2, t, 1]
        coeffs = multiply_vector(M, T)
        P0, T0, T1, P1 = points
        x = coeffs[0] * P0.x + coeffs[1] * T0.x + coeffs[2] * T1.x + coeffs[3] * P1.x
        y = coeffs[0] * P0.y + coeffs[1] * T0.y + coeffs[2] * T1.y + coeffs[3] * P1.y
        yield Pixel(Point(int(round(x)), int(round(y))))

name = "Эрмит"

