import math

def fill_scanline_basic(points):
    if len(points) < 3:
        return []

    n = len(points)
    pixels = []
    pixel_set = set()

    def add_pixel(x, y):
        if (x, y) not in pixel_set:
            pixel_set.add((x, y))
            pixels.append((x, y, 1.0))

    ys = [int(round(p[1])) for p in points]
    min_y = min(ys)
    max_y = max(ys)

    for y in range(min_y, max_y):
        crossings = []

        for i in range(n):
            x1, y1 = points[i][0], int(round(points[i][1]))
            x2, y2 = points[(i + 1) % n][0], int(round(points[(i + 1) % n][1]))

            if y1 == y2:
                continue

            if y1 < y2:
                y_min, y_max = y1, y2
                x_start = x1
                dx = (x2 - x1) / (y2 - y1)
            else:
                y_min, y_max = y2, y1
                x_start = x2
                dx = (x1 - x2) / (y1 - y2)

            # правило [y_min, y_max)
            if y < y_min or y >= y_max:
                continue

            x = x_start + (y - y_min) * dx
            crossings.append(x)

        crossings.sort()

        for i in range(0, len(crossings), 2):
            if i + 1 >= len(crossings):
                break

            x1 = math.ceil(crossings[i])
            x2 = math.floor(crossings[i + 1])

            for x in range(x1, x2 + 1):
                add_pixel(x, y)

    return pixels


def fill_scanline_with_aet(points):
    if len(points) < 3:
        return []

    n = len(points)
    pixels = []
    pixel_set = set()

    def add_pixel(x, y):
        if (x, y) not in pixel_set:
            pixel_set.add((x, y))
            pixels.append((x, y, 1.0))

    ys = [int(round(p[1])) for p in points]
    min_y = min(ys)
    max_y = max(ys)
    et = {}

    for i in range(n):
        x1, y1 = float(points[i][0]), int(round(points[i][1]))
        x2, y2 = float(points[(i + 1) % n][0]), int(round(points[(i + 1) % n][1]))

        if y1 == y2:
            continue

        if y1 < y2:
            y_min, y_max = y1, y2
            x = x1
            inv_slope = (x2 - x1) / (y2 - y1)
        else:
            y_min, y_max = y2, y1
            x = x2
            inv_slope = (x1 - x2) / (y1 - y2)

        if y_min not in et:
            et[y_min] = []

        et[y_min].append({
            'y_max': y_max,
            'x': x,
            'inv_slope': inv_slope
        })

    aet = []

    for y in range(min_y, max_y):
        aet = [e for e in aet if e['y_max'] > y]

        if y in et:
            aet.extend(et[y])

        aet.sort(key=lambda e: e['x'])

        for i in range(0, len(aet), 2):
            if i + 1 >= len(aet):
                break

            x1 = math.ceil(aet[i]['x'])
            x2 = math.floor(aet[i + 1]['x'])

            for x in range(x1, x2 + 1):
                add_pixel(x, y)

        for edge in aet:
            edge['x'] += edge['inv_slope']

    return pixels