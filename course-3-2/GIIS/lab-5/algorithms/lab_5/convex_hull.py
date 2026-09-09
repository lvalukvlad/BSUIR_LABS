import math
name = "Выпуклая оболочка"

def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def distance_squared(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

def graham_scan(points):
    if len(points) < 3:
        return points

    points = list(set(points))
    pivot = min(points, key=lambda p: (p[1], p[0]))
    sorted_points = sorted(points, key=lambda p: (
        0 if p == pivot else 1,
        math.atan2(p[1] - pivot[1], p[0] - pivot[0])
    ))
    
    stack = [sorted_points[0], sorted_points[1]]
    for i in range(2, len(sorted_points)):
        while len(stack) > 1 and cross_product(stack[-2], stack[-1], sorted_points[i]) <= 0:
            stack.pop()
        stack.append(sorted_points[i])
    return stack

def jarvis_march(points):
    if len(points) < 3:
        return points

    points = list(set(points))
    leftmost = min(points, key=lambda p: p[0])
    hull = []
    current = leftmost
    
    while True:
        hull.append(current)
        next_point = points[0]
        for point in points:
            if next_point == current:
                next_point = point
                continue

            cp = cross_product(current, next_point, point)
            if cp < 0 or (cp == 0 and distance_squared(current, point) > distance_squared(current, next_point)):
                next_point = point
        current = next_point
        if current == leftmost:
            break
    
    return hull

def draw_hull(hull_points):
    if len(hull_points) < 2:
        return []

    pixels = []
    n = len(hull_points)
    for i in range(n):
        p1 = hull_points[i]
        p2 = hull_points[(i + 1) % n]
        x0, y0 = int(p1[0]), int(p1[1])
        x1, y1 = int(p2[0]), int(p2[1])
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            pixels.append((x0, y0, 1.0))
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    return pixels




