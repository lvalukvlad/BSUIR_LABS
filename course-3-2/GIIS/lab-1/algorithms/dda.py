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
    dx = x1 - x0 # Δx = x2 - x1
    dy = y1 - y0 # Δy = y2 - y1
    steps = max(abs(dx), abs(dy)) # Шаг 1 алгоритма: Длина = Max(|x2-x1|, |y2-y1|)

    if steps == 0:
        yield Pixel(Point(x0, y0)) # позволяет рисовать линию пошагово
        return
    # Шаг 2:
    x_inc = dx / steps # dx = (x2-x1)/Длина
    y_inc = dy / steps # dy = (y2-y1)/Длина
    x, y = float(x0), float(y0) # Использование вещественных чисел

    # Шаг 3: Integer(x) — округление до целого
    for _ in range(steps + 1):
        yield Pixel(Point(round(x), round(y)))
        x += x_inc # x(i+1) = x(i) + dx
        y += y_inc # y(i+1) = y(i) + dy


name = "ЦДА"