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


def _fpart(x):
    return x - math.floor(x)


def _rfpart(x):
    return 1 - _fpart(x)


def generate(x0, y0, x1, y1):
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 0

    xend = round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = _rfpart(x0 + 0.5)
    xpxl1 = xend
    ypxl1 = math.floor(yend)

    if steep:
        yield Pixel(Point(ypxl1, xpxl1), _rfpart(yend) * xgap)
        yield Pixel(Point(ypxl1 + 1, xpxl1), _fpart(yend) * xgap)
    else:
        yield Pixel(Point(xpxl1, ypxl1), _rfpart(yend) * xgap)
        yield Pixel(Point(xpxl1, ypxl1 + 1), _fpart(yend) * xgap)

    intery = yend + gradient

    for x in range(xpxl1 + 1, round(x1)):
        if steep:
            yield Pixel(Point(math.floor(intery), x), _rfpart(intery))
            yield Pixel(Point(math.floor(intery) + 1, x), _fpart(intery))
        else:
            yield Pixel(Point(x, math.floor(intery)), _rfpart(intery))
            yield Pixel(Point(x, math.floor(intery) + 1), _fpart(intery))
        intery += gradient

    xend = round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = _fpart(x1 + 0.5)
    xpxl2 = xend
    ypxl2 = math.floor(yend)

    if steep:
        yield Pixel(Point(ypxl2, xpxl2), _rfpart(yend) * xgap)
        yield Pixel(Point(ypxl2 + 1, xpxl2), _fpart(yend) * xgap)
    else:
        yield Pixel(Point(xpxl2, ypxl2), _rfpart(yend) * xgap)
        yield Pixel(Point(xpxl2, ypxl2 + 1), _fpart(yend) * xgap)


name = "Ву"