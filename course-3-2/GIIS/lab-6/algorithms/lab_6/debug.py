def fill_scanline_basic_debug(points):
    if len(points) < 3:
        return [], []

    pixels = []
    steps = []

    ys = [p[1] for p in points]
    min_y = min(ys)
    max_y = max(ys)

    n = len(points)

    for y in range(min_y, max_y + 1):
        crossings = []

        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]

            if y1 == y2:
                continue

            lo, hi = (y1, y2) if y1 < y2 else (y2, y1)

            if y < lo or y > hi:
                continue

            is_hi = (y == hi)

            is_local_max = False
            is_local_min = False
            
            if is_hi:
                if y2 > y1:
                    v_idx = (i + 1) % n
                else:
                    v_idx = i

                prev_y = points[(v_idx - 1) % n][1]
                next_y = points[(v_idx + 1) % n][1]

                if prev_y < y and next_y < y:
                    is_local_max = True
            
            is_lo = (y == lo)
            if is_lo and y2 > y1:
                v_idx = i
                prev_y = points[(v_idx - 1) % n][1]
                next_y = points[(v_idx + 1) % n][1]
                if prev_y > y and next_y > y:
                    continue
            
            if is_lo and y2 < y1:
                v_idx = (i + 1) % n
                prev_y = points[(v_idx - 1) % n][1]
                next_y = points[(v_idx + 1) % n][1]
                if prev_y > y and next_y > y:
                    is_local_min = True
            
            if is_local_max:
                x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                crossings.append(x)
                continue
            
            if is_local_min:
                x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                crossings.append(x)
                crossings.append(x)
                continue

            x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            crossings.append(x)

        crossings.sort()

        step = {
            'y': y,
            'intersections': [round(c, 2) for c in crossings],
            'intervals': [],
            'pixels': []
        }

        i = 0
        while i < len(crossings) - 1:
            x1 = int(round(crossings[i]))
            x2 = int(round(crossings[i + 1]))
            if x1 > x2:
                x1, x2 = x2, x1

            interval_pixels = []
            for x in range(x1, x2 + 1):
                pixels.append((x, y, 1.0))
                interval_pixels.append((x, y))

            step['intervals'].append((x1, x2))
            step['pixels'].append(interval_pixels)
            i += 2

        steps.append(step)

    seen = set()
    unique_pixels = []
    for p in pixels:
        key = (p[0], p[1])
        if key not in seen:
            seen.add(key)
            unique_pixels.append(p)
    return unique_pixels, steps


def fill_scanline_aet_debug(points):
    if len(points) < 3:
        return [], []

    n = len(points)
    pixels = []
    steps = []

    ys = [p[1] for p in points]
    min_y = min(ys)
    max_y = max(ys)

    et = {}
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]

        if y1 == y2:
            continue

        if y1 < y2:
            y_min, y_max = y1, y2
            x_at_y_min = float(x1)
            upper_v_idx = (i + 1) % n
            lower_v_idx = i
        else:
            y_min, y_max = y2, y1
            x_at_y_min = float(x2)
            upper_v_idx = i
            lower_v_idx = (i + 1) % n

        inv_slope = (x2 - x1) / (y2 - y1)

        if y_min not in et:
            et[y_min] = []
        et[y_min].append({
            'y_min': y_min,
            'y_max': y_max,
            'x': x_at_y_min,
            'inv_slope': inv_slope,
            'upper_v_idx': upper_v_idx,
            'lower_v_idx': lower_v_idx
        })

    aet = []

    for y in range(min_y, max_y + 1):
        aet = [e for e in aet if e['y_max'] >= y]

        if y in et:
            for edge in et[y]:
                aet.append(edge)

        aet_before = [(round(e['x'], 1), e['y_max']) for e in aet]

        crossings = []
        for edge in aet:
            is_local_max = False
            is_local_min = False
            
            if y == edge['y_max']:
                v_idx = edge['upper_v_idx']
                prev_y = points[(v_idx - 1) % n][1]
                next_y = points[(v_idx + 1) % n][1]
                if prev_y < y and next_y < y:
                    is_local_max = True
            
            if y == edge['y_min'] and edge['inv_slope'] > 0:
                v_idx = (edge['upper_v_idx'] - 1) % n
                prev_y = points[(v_idx - 1) % n][1]
                next_y = points[(v_idx + 1) % n][1]
                if prev_y > y and next_y > y:
                    continue
            
            if y == edge['y_min'] and edge['inv_slope'] < 0:
                v_idx = edge['lower_v_idx']
                prev_y = points[(v_idx - 1) % n][1]
                next_y = points[(v_idx + 1) % n][1]
                if prev_y > y and next_y > y:
                    is_local_min = True
            
            if is_local_max:
                crossings.append(edge['x'])
                continue
            
            if is_local_min:
                crossings.append(edge['x'])
                crossings.append(edge['x'])
                continue
            
            crossings.append(edge['x'])
        
        aet_after = [(round(e['x'], 1), e['y_max']) for e in aet]

        crossings.sort()

        step = {
            'y': y,
            'aet_before': aet_before,
            'aet_after': aet_after,
            'intersections': [round(c, 2) for c in crossings],
            'intervals': [],
            'pixels': []
        }

        i = 0
        while i < len(crossings) - 1:
            x1 = int(round(crossings[i]))
            x2 = int(round(crossings[i + 1]))
            if x1 > x2:
                x1, x2 = x2, x1

            interval_pixels = []
            for x in range(x1, x2 + 1):
                pixels.append((x, y, 1.0))
                interval_pixels.append((x, y))

            step['intervals'].append((x1, x2))
            step['pixels'].append(interval_pixels)
            i += 2

        steps.append(step)

        for edge in aet:
            edge['x'] += edge['inv_slope']

    seen = set()
    unique_pixels = []
    for p in pixels:
        key = (p[0], p[1])
        if key not in seen:
            seen.add(key)
            unique_pixels.append(p)
    return unique_pixels, steps


def fill_seed_simple_debug(points, seed):
    fill_color = 0.5
    boundary_color = 1.0

    min_x = min(int(p[0]) for p in points)
    max_x = max(int(p[0]) for p in points)
    min_y = min(int(p[1]) for p in points)
    max_y = max(int(p[1]) for p in points)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    bitmap = [[0.0 for _ in range(width)] for _ in range(height)]

    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]

        x0 = int(p1[0]) - min_x
        y0 = int(p1[1]) - min_y
        x1 = int(p2[0]) - min_x
        y1 = int(p2[1]) - min_y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                bitmap[y0][x0] = boundary_color
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        if 0 <= x1 < width and 0 <= y1 < height:
            bitmap[y1][x1] = boundary_color

    stack = [(seed[0] - min_x, seed[1] - min_y)]
    pixels = []
    boundary_pixels = []
    visited = set()
    steps = []
    step_num = 0

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if bitmap[y][x] != 0.0:
            if bitmap[y][x] == boundary_color:
                boundary_pixels.append((x + min_x, y + min_y, 1.0))
            continue

        bitmap[y][x] = fill_color
        pixels.append((x + min_x, y + min_y, 1.0))
        step_num += 1

        step = {
            'step': step_num,
            'current': (x + min_x, y + min_y),
            'filled': [(x + min_x, y + min_y)],
            'stack_size': len(stack)
        }
        steps.append(step)

        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))

    pixels.extend(boundary_pixels)
    return pixels, steps


def fill_seed_scanline_debug(points, seed):
    min_x = min(int(p[0]) for p in points)
    max_x = max(int(p[0]) for p in points)
    min_y = min(int(p[1]) for p in points)
    max_y = max(int(p[1]) for p in points)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    bitmap = [[0.0 for _ in range(width)] for _ in range(height)]
    boundary_pixels = []

    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]

        x0 = int(p1[0]) - min_x
        y0 = int(p1[1]) - min_y
        x1 = int(p2[0]) - min_x
        y1 = int(p2[1]) - min_y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                bitmap[y0][x0] = 1.0
                boundary_pixels.append((x0 + min_x, y0 + min_y, 1.0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    stack = [(seed[0] - min_x, seed[1] - min_y)]
    pixels = []
    visited = set()
    steps = []
    step_num = 0

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if (x, y) in visited:
            continue
        visited.add((x, y))

        if bitmap[y][x] != 0.0:
            continue

        left = x
        while left > 0 and bitmap[y][left - 1] == 0.0:
            left -= 1

        right = x
        while right < width - 1 and bitmap[y][right + 1] == 0.0:
            right += 1

        interval_filled = []
        for px in range(left, right + 1):
            if bitmap[y][px] == 0.0:
                bitmap[y][px] = 0.5
                pixels.append((px + min_x, y + min_y, 1.0))
                interval_filled.append((px + min_x, y + min_y))

        new_seeds = []
        for px in range(left, right + 1):
            if y > 0 and bitmap[y - 1][px] == 0.0:
                stack.append((px, y - 1))
                new_seeds.append((px + min_x, y - 1 + min_y))
            if y < height - 1 and bitmap[y + 1][px] == 0.0:
                stack.append((px, y + 1))
                new_seeds.append((px + min_x, y + 1 + min_y))

        step_num += 1
        step = {
            'step': step_num,
            'current': (x + min_x, y + min_y),
            'interval': (left + min_x, right + min_x),
            'filled': interval_filled,
            'new_seeds': new_seeds,
            'stack_size': len(stack)
        }
        steps.append(step)

    pixels.extend(boundary_pixels)

    seen = set()
    unique_pixels = []
    for p in pixels:
        key = (p[0], p[1])
        if key not in seen:
            seen.add(key)
            unique_pixels.append(p)
    return unique_pixels, steps
