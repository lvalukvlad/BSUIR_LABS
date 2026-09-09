import state
from ..debug_panel import step
import math

def draw_shape_preview():
    cx, cy = state.start_point
    px, py = state.preview_end
    import math
    r = int(math.sqrt((px - cx) ** 2 + (py - cy) ** 2))
    if r == 0:
        r = 1

    if state.algorithm_name == "Окружность":
        args = (cx, cy, r)
    elif state.algorithm_name == "Эллипс":
        rx = r
        ry = int(r * 0.6)
        args = (cx, cy, rx, ry)
    elif state.algorithm_name == "Парабола":
        args = (cx, cy, px, py)
    elif state.algorithm_name == "Гипербола":
        args = (cx, cy, px, py)
    else:
        args = (cx, cy, r)

    pixels = list(state.current_algorithm(*args))
    for pixel in pixels:
        from ..canvas import draw_pixel
        draw_pixel(pixel, '#90EE90')

def handle_shape_click(point):
    from ..canvas import update_status, clear_selection, redraw
    if state.start_point is None:
        state.start_point = point
        update_status(f"Центр: {point}. Кликните для размера.")
    else:
        cx, cy = state.start_point
        px, py = point

        r = int(math.sqrt((px - cx) ** 2 + (py - cy) ** 2))
        if r == 0:
            r = 1

        if state.algorithm_name == "Окружность":
            args = (cx, cy, r)
        elif state.algorithm_name == "Эллипс":
            ry = int(r * 0.6)
            args = (cx, cy, r, ry)
        elif state.algorithm_name == "Парабола":
            args = (cx, cy, px, py)
        elif state.algorithm_name == "Гипербола":
            args = (cx, cy, px, py)
        else:
            args = (cx, cy, r)

        if state.mode == "normal":
            pixels = list(state.current_algorithm(*args))
            state.all_pixels.extend(pixels)
            clear_selection()
            update_status(f"Фигура нарисована: {len(pixels)} пикселей")
        else:
            state.debug_generator = state.current_algorithm(*args)
            state.debug_pixels = []
            state.debug_step = 0
            step()

        redraw()

