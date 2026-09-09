import state


def draw_curve_preview():
    if not state.lab_3_points:
        return

    points = state.lab_3_points
    algo_name = state.algorithm_name

    from ..canvas import grid_to_screen, draw_pixel

    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        x1, y1 = grid_to_screen(p1[0], p1[1])
        x2, y2 = grid_to_screen(p2[0], p2[1])
        c = state.canvas
        c.create_line(x1, y1, x2, y2, fill='#CCCCCC', dash=(4, 4))

    if algo_name in ("Эрмит", "Безье", "B-сплайн"):
        try:
            algo_module, PointClass = get_algorithm_module()
            algo_points = [PointClass(float(p[0]), float(p[1])) for p in points]
            pixels = list(algo_module.generate(algo_points))
            for pixel in pixels:
                draw_pixel(pixel, '#90EE90')
        except Exception as e:
            pass


def get_algorithm_module():
    if state.algorithm_name == "Эрмит":
        from algorithms.lab_3 import hermite
        from algorithms.lab_3.hermite import Point
        return hermite, Point
    elif state.algorithm_name == "Безье":
        from algorithms.lab_3 import bezier
        from algorithms.lab_3.bezier import Point
        return bezier, Point
    elif state.algorithm_name == "B-сплайн":
        from algorithms.lab_3 import bspline
        from algorithms.lab_3.bspline import Point
        return bspline, Point
    else:
        from algorithms.lab_3 import bezier
        from algorithms.lab_3.bezier import Point
        return bezier, Point


def handle_curve_click(point):
    from ..canvas import update_status, redraw

    if state.adjustment_mode:
        if state.lab_3_points:
            closest_idx = find_closest_point(point)
            if closest_idx is not None:
                state.lab_3_points[closest_idx] = point
                update_status(f"Точка {closest_idx} перемещена в {point}")
                redraw()
        return

    state.lab_3_points.append(point)

    algo_name = state.algorithm_name

    if algo_name == "Эрмит":
        required = 4
        hint = "Эрмит: P0, T0, T1, P1"
    elif algo_name == "Безье":
        required = 4
        hint = "Безье: введите 4 контрольные точки"
    elif algo_name == "B-сплайн":
        required = 4
        hint = "B-сплайн: минимум 4 точки (добавляйте для непрерывной кривой)"
    else:
        required = 4
        hint = "Выберите алгоритм"

    if len(state.lab_3_points) >= required:
        try:
            algo_module, PointClass = get_algorithm_module()
            algo_points = [PointClass(float(p[0]), float(p[1])) for p in state.lab_3_points]
            pixels = list(algo_module.generate(algo_points))
            state.all_pixels.extend(pixels)

            last_point = state.lab_3_points[-1]
            state.lab_3_points = [last_point]

            update_status(f"Кривая построена: {len(pixels)} пикселей. Добавьте точки для стыковки.")
        except Exception as e:
            update_status(f"Ошибка: {str(e)}")
    else:
        points_needed = required - len(state.lab_3_points)
        update_status(f"{hint}. Осталось: {points_needed}")

    redraw()


def find_closest_point(point):
    if not state.lab_3_points:
        return None

    px, py = point
    closest_idx = None
    min_dist = float('inf')

    for i, p in enumerate(state.lab_3_points):
        dist = ((p[0] - px) ** 2 + (p[1] - py) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            closest_idx = i

    if min_dist < 5:
        return closest_idx
    return None


def draw_control_points():
    if not state.lab_3_points:
        return

    from ..canvas import grid_to_screen

    size = state.CELL_SIZE * 3

    for i, point in enumerate(state.lab_3_points):
        sx, sy = grid_to_screen(point[0], point[1])
        color = '#FF6600' if i < 4 else '#0066CC'
        state.canvas.create_rectangle(sx, sy, sx+size, sy+size, fill=color, outline='black')
