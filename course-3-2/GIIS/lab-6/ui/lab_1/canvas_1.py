import state
from ..debug_panel import step

def draw_line_preview():
    x0, y0 = state.start_point
    x1, y1 = state.preview_end
    pixels = list(state.current_algorithm(x0, y0, x1, y1))
    for pixel in pixels:
        from ..canvas import draw_pixel
        draw_pixel(pixel, '#90EE90')

def handle_line_click(point):
    from ..canvas import update_status, clear_selection, redraw
    if state.start_point is None:
        state.start_point = point
        update_status(f"Начало: {point}. Кликните на конец отрезка.")
    else:
        state.end_point = point
        x0, y0 = state.start_point
        x1, y1 = state.end_point

        if state.mode == "normal":
            pixels = list(state.current_algorithm(x0, y0, x1, y1))
            state.all_pixels.extend(pixels)
            clear_selection()
            update_status(f"Отрезок нарисован: {len(pixels)} пикселей")
        else:
            state.debug_generator = state.current_algorithm(x0, y0, x1, y1)
            state.debug_pixels = []
            state.debug_step = 0
            step()

        redraw()