def fill_seed_simple(points, seed):
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
        
        stack.append((x + 1, y))
        stack.append((x - 1, y))
        stack.append((x, y + 1))
        stack.append((x, y - 1))
    
    pixels.extend(boundary_pixels)
    return pixels


def fill_seed_scanline(points, seed):
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
        
        for px in range(left, right + 1):
            if bitmap[y][px] == 0.0:
                bitmap[y][px] = 0.5
                pixels.append((px + min_x, y + min_y, 1.0))
        
        for px in range(left, right + 1):
            if y > 0 and bitmap[y - 1][px] == 0.0:
                stack.append((px, y - 1))
            if y < height - 1 and bitmap[y + 1][px] == 0.0:
                stack.append((px, y + 1))
    
    pixels.extend(boundary_pixels)
    return pixels
