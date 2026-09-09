import math


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


def _edges_of_triangle(t):
    return [
        (t[0], t[1]),
        (t[1], t[2]),
        (t[2], t[0]),
    ]


def _normalize_edge(e):
    return (min(e[0], e[1]), max(e[0], e[1]))


def voronoi(points, triangles):
    if not triangles:
        return [], []

    vertices = []
    tri_cc = {}
    for i, t in enumerate(triangles):
        cc = circumcenter(t[0], t[1], t[2])
        if cc is not None:
            vertices.append(cc)
            tri_cc[i] = cc

    edge_to_tri = {}
    for i, t in enumerate(triangles):
        for e in _edges_of_triangle(t):
            ne = _normalize_edge(e)
            edge_to_tri.setdefault(ne, []).append(i)

    edges = []
    BIG = 1e6

    for ne, tri_indices in edge_to_tri.items():
        if len(tri_indices) == 2:
            if tri_indices[0] in tri_cc and tri_indices[1] in tri_cc:
                edges.append((tri_cc[tri_indices[0]], tri_cc[tri_indices[1]]))
        elif len(tri_indices) == 1 and tri_indices[0] in tri_cc:
            cc = tri_cc[tri_indices[0]]
            a, b = ne
            mx = (a[0] + b[0]) / 2.0
            my = (a[1] + b[1]) / 2.0
            dx = mx - cc[0]
            dy = my - cc[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1e-10:
                dx /= dist
                dy /= dist
            else:
                dx, dy = 0.0, 1.0
            t = triangles[tri_indices[0]]
            third = next(v for v in t if v != a and v != b)
            if dx * (third[0] - mx) + dy * (third[1] - my) > 0:
                dx, dy = -dx, -dy
            far = (cc[0] + dx * BIG, cc[1] + dy * BIG)
            edges.append((cc, far))

    return edges, vertices


debug_steps = []


def voronoi_debug(points, triangles):
    global debug_steps
    debug_steps = []
    if not triangles:
        return [], []

    vertices = []
    tri_cc = {}
    for i, t in enumerate(triangles):
        cc = circumcenter(t[0], t[1], t[2])
        if cc is not None:
            vertices.append(cc)
            tri_cc[i] = cc
            debug_steps.append({
                'description': f'Вершина {len(vertices)}: '
                               f'({cc[0]:.1f}, {cc[1]:.1f})',
                'edges': _build_edges(tri_cc, triangles),
                'vertices': list(vertices),
            })

    edge_to_tri = {}
    for i, t in enumerate(triangles):
        for e in _edges_of_triangle(t):
            ne = _normalize_edge(e)
            edge_to_tri.setdefault(ne, []).append(i)

    edges = []
    BIG = 1e6

    for ne, tri_indices in edge_to_tri.items():
        if len(tri_indices) == 2:
            if tri_indices[0] in tri_cc and tri_indices[1] in tri_cc:
                e = (tri_cc[tri_indices[0]], tri_cc[tri_indices[1]])
                edges.append(e)
                debug_steps.append({
                    'description': f'Ребро Вороного {len(edges)} '
                                   f'(внутреннее)',
                    'edges': list(edges),
                    'vertices': list(vertices),
                })
        elif len(tri_indices) == 1 and tri_indices[0] in tri_cc:
            cc = tri_cc[tri_indices[0]]
            a, b = ne
            mx = (a[0] + b[0]) / 2.0
            my = (a[1] + b[1]) / 2.0
            dx = mx - cc[0]
            dy = my - cc[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1e-10:
                dx /= dist
                dy /= dist
            else:
                dx, dy = 0.0, 1.0
            t = triangles[tri_indices[0]]
            third = next(v for v in t if v != a and v != b)
            if dx * (third[0] - mx) + dy * (third[1] - my) > 0:
                dx, dy = -dx, -dy
            far = (cc[0] + dx * BIG, cc[1] + dy * BIG)
            edges.append((cc, far))
            debug_steps.append({
                'description': f'Ребро Вороного {len(edges)} '
                               f'(граничная \u2192 \u221e)',
                'edges': list(edges),
                'vertices': list(vertices),
            })

    debug_steps.append({
        'description': f'Готово: {len(edges)} рёбер',
        'edges': list(edges),
        'vertices': list(vertices),
    })
    return edges, vertices


def _build_edges(tri_cc, triangles):
    edge_to_tri = {}
    for i, t in enumerate(triangles):
        for e in _edges_of_triangle(t):
            ne = _normalize_edge(e)
            edge_to_tri.setdefault(ne, []).append(i)

    edges = []
    BIG = 1e6
    for ne, tri_indices in edge_to_tri.items():
        if len(tri_indices) == 2:
            if tri_indices[0] in tri_cc and tri_indices[1] in tri_cc:
                edges.append((tri_cc[tri_indices[0]],
                              tri_cc[tri_indices[1]]))
        elif len(tri_indices) == 1 and tri_indices[0] in tri_cc:
            cc = tri_cc[tri_indices[0]]
            a, b = ne
            mx = (a[0] + b[0]) / 2.0
            my = (a[1] + b[1]) / 2.0
            dx = mx - cc[0]
            dy = my - cc[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1e-10:
                dx /= dist
                dy /= dist
            else:
                dx, dy = 0.0, 1.0
            t = triangles[tri_indices[0]]
            third = next(v for v in t if v != a and v != b)
            if dx * (third[0] - mx) + dy * (third[1] - my) > 0:
                dx, dy = -dx, -dy
            far = (cc[0] + dx * BIG, cc[1] + dy * BIG)
            edges.append((cc, far))
    return edges
