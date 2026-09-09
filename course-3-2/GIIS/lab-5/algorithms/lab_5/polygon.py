import math
name = "Полигон"

def cross_product(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def is_convex(points):
    if len(points) < 3:
        return False

    n = len(points)
    sign = 0
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        cp = cross_product(p1, p2, p3)
        if cp != 0:
            if sign == 0:
                sign = 1 if cp > 0 else -1
            elif (cp > 0 and sign < 0) or (cp < 0 and sign > 0):
                return False
    return True

def get_internal_normals(points):
    if len(points) < 3:
        return []
    normals = []
    n = len(points)
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            normals.append((0, 0, p1[0], p1[1]))
            continue

        nx = -dy / length
        ny = dx / length
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        normals.append((nx, ny, mid_x, mid_y))
    return normals

def point_on_segment(px, py, x1, y1, x2, y2):
    min_x, max_x = min(x1, x2), max(x1, x2)
    min_y, max_y = min(y1, y2), max(y1, y2)
    if min_x <= px <= max_x and min_y <= py <= max_y:
        return True
    return False


def dist_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
    
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    near_x = x1 + t * dx
    near_y = y1 + t * dy
    return math.sqrt((px - near_x) ** 2 + (py - near_y) ** 2)


def build_polygon(points):
    if len(points) < 3:
        return []

    pixels = []
    n = len(points)
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
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
