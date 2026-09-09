import math
name = "Принадлежность точки"

def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    if n < 3:
        return False
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def draw_point_marker(point, inside):
    x, y = int(point[0]), int(point[1])
    pixels = []
    color_val = 1.0 if inside else 0.3
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            if dx * dx + dy * dy <= 9:
                pixels.append((x + dx, y + dy, color_val))
    return pixels
