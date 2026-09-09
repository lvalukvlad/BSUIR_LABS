import math


def normalize_triangle(tri):
    pts = list(tri)
    pts.sort(key=lambda x: (x[0], x[1]))
    return tuple(pts)


def circumcenter(a, b, c):
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    cx, cy = c[0], c[1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-10:
        return None
    ux = ((ax**2 + ay**2) * (by - cy) +
          (bx**2 + by**2) * (cy - ay) +
          (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) +
          (bx**2 + by**2) * (ax - cx) +
          (cx**2 + cy**2) * (bx - ax)) / d
    return (ux, uy)


def cross_sign(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _convex_hull(points):
    n = len(points)
    if n < 3:
        return list(range(n))
    start = min(range(n), key=lambda i: (points[i][0], points[i][1]))
    hull = [start]
    current = start
    while True:
        candidate = (current + 1) % n
        for j in range(n):
            if j == current:
                continue
            cr = cross_sign(points[current], points[candidate], points[j])
            if cr < -1e-10:
                candidate = j
            elif abs(cr) < 1e-10:
                d_cur = ((points[candidate][0] - points[current][0])**2 +
                         (points[candidate][1] - points[current][1])**2)
                d_j = ((points[j][0] - points[current][0])**2 +
                       (points[j][1] - points[current][1])**2)
                if d_j > d_cur:
                    candidate = j
        if candidate == start:
            break
        hull.append(candidate)
        current = candidate
    return hull


def _find_conjugate(a, b, pts, exclude_indices):
    best_idx = None
    best_r = float('inf')
    pa, pb = pts[a], pts[b]
    for i in range(len(pts)):
        if i == a or i == b or i in exclude_indices:
            continue
        p = pts[i]
        cr = cross_sign(pa, pb, p)
        if abs(cr) < 1e-10:
            continue
        cc = circumcenter(pa, pb, p)
        if cc is None:
            continue
        r = math.sqrt((cc[0] - pa[0])**2 + (cc[1] - pa[1])**2)
        if r >= best_r:
            continue
        empty = True
        for j in range(len(pts)):
            if j == a or j == b or j == i:
                continue
            q = pts[j]
            if (q[0] - cc[0])**2 + (q[1] - cc[1])**2 < r**2 - 1e-9:
                cr_q = cross_sign(pa, pb, q)
                if cr_q * cr > 0:
                    empty = False
                    break
        if empty:
            best_idx = i
            best_r = r
    return best_idx


debug_steps = []


def delaunay(points):
    if len(points) < 3:
        return []
    pts = [(float(x), float(y)) for x, y in points]
    hull = _convex_hull(pts)
    n = len(pts)
    edge_tris = {}
    living = set()
    for i in range(len(hull)):
        a, b = hull[i], hull[(i + 1) % len(hull)]
        living.add((a, b))
    triangles = []
    seen = set()
    max_iter = n * n * 4
    for _ in range(max_iter):
        if not living:
            break
        edge = next(iter(living))
        living.discard(edge)
        a, b = edge
        key_ab = (min(a, b), max(a, b))
        existing = edge_tris.get(key_ab, set())
        if len(existing) >= 2:
            living.discard((b, a))
            continue
        exclude = set(existing)
        c = _find_conjugate(a, b, pts, exclude)
        if c is None:
            continue
        t = normalize_triangle((pts[a], pts[b], pts[c]))
        if t in seen:
            continue
        seen.add(t)
        triangles.append(t)
        edge_tris.setdefault(key_ab, set()).add(c)
        if len(edge_tris[key_ab]) >= 2:
            living.discard((b, a))
        for e in [(a, c), (b, c)]:
            ke = (min(e[0], e[1]), max(e[0], e[1]))
            edge_tris.setdefault(ke, set()).add(c)
            if len(edge_tris[ke]) >= 2:
                living.discard(e)
                living.discard((min(e[0], e[1]), max(e[0], e[1])))
            else:
                if e not in living and (e[1], e[0]) not in living:
                    living.add(e)
    return triangles


def delaunay_debug(points):
    global debug_steps
    debug_steps = []
    if len(points) < 3:
        return []
    pts = [(float(x), float(y)) for x, y in points]
    hull = _convex_hull(pts)
    n = len(pts)
    edge_tris = {}
    living = set()
    for i in range(len(hull)):
        a, b = hull[i], hull[(i + 1) % len(hull)]
        living.add((a, b))
    hull_edges = [(pts[a], pts[b]) for a, b in living]
    debug_steps.append({
        'description': 'Шаг 1: Инициализация — '
                       'выпуклая оболочка, все рёбра «живые»',
        'triangles': [],
        'living': list(living),
        'hull_edges': hull_edges,
    })
    triangles = []
    seen = set()
    step_num = 2
    max_iter = n * n * 4
    for _ in range(max_iter):
        if not living:
            break
        edge = next(iter(living))
        living.discard(edge)
        a, b = edge
        key_ab = (min(a, b), max(a, b))
        existing = edge_tris.get(key_ab, set())
        if len(existing) >= 2:
            living.discard((b, a))
            continue
        exclude = set(existing)
        c = _find_conjugate(a, b, pts, exclude)
        if c is None:
            debug_steps.append({
                'description':
                    f'Шаг {step_num}: ребро ({a},{b})'
                    f' — сопряжённая точка не найдена',
                'triangles': list(triangles),
                'living': list(living),
            })
            step_num += 1
            continue
        t = normalize_triangle((pts[a], pts[b], pts[c]))
        if t in seen:
            continue
        seen.add(t)
        triangles.append(t)
        edge_tris.setdefault(key_ab, set()).add(c)
        if len(edge_tris[key_ab]) >= 2:
            living.discard((b, a))
        new_edges = [(a, c), (b, c)]
        new_desc = []
        for e in new_edges:
            new_desc.append(f'({e[0]},{e[1]})')
            ke = (min(e[0], e[1]), max(e[0], e[1]))
            edge_tris.setdefault(ke, set()).add(c)
            if len(edge_tris[ke]) >= 2:
                living.discard(e)
                living.discard((min(e[0], e[1]), max(e[0], e[1])))
            else:
                if e not in living and (e[1], e[0]) not in living:
                    living.add(e)
        debug_steps.append({
            'description':
                f'Шаг {step_num}: треугольник'
                f' ({a},{b},{c}), рёбра'
                f' {", ".join(new_desc)}',
            'triangles': list(triangles),
            'living': list(living),
        })
        step_num += 1
    debug_steps.append({
        'description': f'Готово: {len(triangles)} треугольников',
        'triangles': list(triangles),
        'living': [],
    })
    return triangles
