import state
from algorithms.lab_5 import point_in_polygon


def handle_fill_click(point):
    if not state.polygons:
        state.status_label.config(text="Сначала постройте полигон в режиме Построение полигонов")
        return
    
    found_polygons = []
    for i, poly_data in enumerate(state.polygons):
        if isinstance(poly_data, dict):
            points = poly_data['points']
        else:
            points = poly_data
        
        if point_in_polygon.point_in_polygon(point, points):
            found_polygons.append(i)
    
    if not found_polygons:
        state.status_label.config(text="Кликните внутри полигона")
        return
    
    if state.fill_polygon_index in found_polygons:
        current_idx = found_polygons.index(state.fill_polygon_index)
        next_idx = (current_idx + 1) % len(found_polygons)
        state.fill_polygon_index = found_polygons[next_idx]
    else:
        state.fill_polygon_index = found_polygons[0]
    
    if state.fill_algorithm in ['seed_simple', 'seed_scanline']:
        state.fill_seed_point = point
        state.status_label.config(text=f"Затравка: {point}. Нажмите 'Заполнить'")
    else:
        state.status_label.config(text=f"Выбран полигон #{state.fill_polygon_index + 1}. Нажмите 'Заполнить'")
    
    from ui.canvas import redraw
    redraw()


def draw_filled_pixels():
    c = state.canvas
    from ui.canvas import grid_to_screen
    
    for pixel in state.filled_pixels:
        x, y, intensity = pixel[0], pixel[1], pixel[2]
        sx, sy = grid_to_screen(x, y)
        size = state.CELL_SIZE - 1
        c.create_rectangle(sx + 2, sy + 2, sx + size, sy + size, fill='#00CC66', outline='')


def draw_fill_seed():
    c = state.canvas
    if state.fill_seed_point:
        from ui.canvas import grid_to_screen
        sx, sy = grid_to_screen(state.fill_seed_point[0], state.fill_seed_point[1])
        c.create_oval(sx-6, sy-6, sx+6, sy+6, fill='red', outline='red', width=2)


def draw_polygon_fill_outline():
    from ui.lab_5.canvas_5 import draw_polygons
    if state.fill_polygon_index is not None:
        draw_polygons()
