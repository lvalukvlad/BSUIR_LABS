import state
from algorithms.lab_5 import polygon as poly_algo
from algorithms.lab_5 import convex_hull
from algorithms.lab_5 import intersection
from algorithms.lab_5 import point_in_polygon
from ..canvas import grid_to_screen, update_status
import math

def draw_polygon_preview():
    if not state.polygon_points:
        return
    points = state.polygon_points
    c = state.canvas
    
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        x1, y1 = grid_to_screen(p1[0], p1[1])
        x2, y2 = grid_to_screen(p2[0], p2[1])
        c.create_line(x1, y1, x2, y2, fill='#FF6600', width=2)
    
    if hasattr(state, 'preview_end') and state.preview_end:
        last_point = points[-1]
        x1, y1 = grid_to_screen(last_point[0], last_point[1])
        x2, y2 = grid_to_screen(state.preview_end[0], state.preview_end[1])
        c.create_line(x1, y1, x2, y2, fill='#FF6600', width=2, dash=(4, 4))
    
    for point in points:
        sx, sy = grid_to_screen(point[0], point[1])
        c.create_oval(sx-4, sy-4, sx+4, sy+4, fill='#FF6600', outline='#333')


def draw_polygons():
    if not state.polygons:
        return
    c = state.canvas
    for idx, poly_data in enumerate(state.polygons):
        if isinstance(poly_data, dict):
            points = poly_data['points']
            color = poly_data.get('color', '#0066CC')
            is_convex = poly_data.get('is_convex', None)
        else:
            points = poly_data
            color = '#0066CC'
            is_convex = None

        is_selected = (idx == state.selected_polygon_index)
        line_color = color
        line_width = 2
        if is_selected:
            line_width = 4
            line_color = '#FF0000'
        
        n = len(points)
        if n < 2:
            continue
        
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            x1, y1 = grid_to_screen(p1[0], p1[1])
            x2, y2 = grid_to_screen(p2[0], p2[1])
            c.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)
        
        for point in points:
            sx, sy = grid_to_screen(point[0], point[1])
            outline = 'green' if is_convex else 'red' if is_convex is False else 'black'
            if is_selected:
                outline = '#FF0000'
            c.create_oval(sx-3, sy-3, sx+3, sy+3, fill=color, outline=outline)
        
        if is_selected:
            sx, sy = grid_to_screen(points[0][0], points[0][1])
            c.create_text(sx, sy-15, text=f"#{idx+1}", fill='#FF0000', font=('Arial', 10, 'bold'))
            c.create_oval(sx-3, sy-3, sx+3, sy+3, fill=color, outline=outline)

def draw_normals():
    if not state.polygons:
        return
    c = state.canvas
    if state.selected_polygon_index is not None and state.selected_polygon_index < len(state.polygons):
        poly_data = state.polygons[state.selected_polygon_index]
        if isinstance(poly_data, dict):
            points = poly_data['points']
        else:
            points = poly_data
        
        normals = poly_algo.get_internal_normals(points)
        for nx, ny, mx, my in normals:
            sx, sy = grid_to_screen(mx, my)
            ex = sx + nx * 40
            ey = sy - ny * 40
            c.create_line(sx, sy, ex, ey, fill='#00AA00', arrow='last')


def draw_intersection():
    if state.polygon_mode != 'intersection':
        return
    
    if state.intersection_segment and state.selected_polygon_index is not None:
        c = state.canvas
        p1 = state.intersection_segment[0]
        p2 = state.intersection_segment[1]
        
        if p2 is None:
            sx, sy = grid_to_screen(p1[0], p1[1])
            c.create_oval(sx-5, sy-5, sx+5, sy+5, fill='red', outline='red', width=2)
            return
        
        x1, y1 = grid_to_screen(p1[0], p1[1])
        x2, y2 = grid_to_screen(p2[0], p2[1])
        c.create_line(x1, y1, x2, y2, fill='#FF6600', width=2, dash=(4, 4))
        c.create_oval(x1-3, y1-3, x1+3, y1+3, fill='red', outline='red')
        c.create_oval(x2-3, y2-3, x2+3, y2+3, fill='red', outline='red')
        poly_data = state.polygons[state.selected_polygon_index]
        if isinstance(poly_data, dict):
            points = poly_data['points']
        else:
            points = poly_data
        intersects = intersection.find_intersections(state.intersection_segment, points)
        
        for point, edge_idx in intersects:
            sx, sy = grid_to_screen(point[0], point[1])
            c.create_oval(sx-6, sy-6, sx+6, sy+6, fill='yellow', outline='black', width=2)

def draw_point_test():
    if state.polygon_mode != 'point_in_polygon':
        return
    
    if state.test_point:
        c = state.canvas
        px, py = state.test_point
        sx, sy = grid_to_screen(px, py)
        if state.selected_polygon_index is not None and state.selected_polygon_index < len(state.polygons):
            poly_data = state.polygons[state.selected_polygon_index]
            if isinstance(poly_data, dict):
                points = poly_data['points']
            else:
                points = poly_data
            inside = point_in_polygon.point_in_polygon(state.test_point, points)
        else:
            inside = False
        
        fill_color = '#00FF00' if inside else '#FF0000'
        outline_color = '#00AA00' if inside else '#AA0000'
        c.create_oval(sx-8, sy-8, sx+8, sy+8, fill=fill_color, outline=outline_color, width=2)
        status = "ВНУТРИ" if inside else "СНАРУЖИ"
        c.create_text(sx, sy-15, text=status, fill=outline_color, font=('Arial', 8, 'bold'))

def find_polygon_at_point(point):
    px, py = point
    for i, poly_data in enumerate(state.polygons):
        if isinstance(poly_data, dict):
            points = poly_data['points']
        else:
            points = poly_data
        if point_in_polygon.point_in_polygon(point, points):
            return i
    return None

def handle_polygon_click(point):
    mode = state.polygon_mode
    if mode == 'build':
        state.polygon_points.append(point)
        if len(state.polygon_points) >= 3:
            from ..canvas import update_status
            points_needed = 3 - len(state.polygon_points)
            if points_needed > 0:
                update_status(f"Добавьте еще {points_needed} точек или нажмите 'Завершить'")
            else:
                update_status(f"Нажмите 'Завершить полигон' для создания")
        else:
            from ..canvas import update_status
            points_needed = 3 - len(state.polygon_points)
            update_status(f"Добавьте еще {points_needed} точек")
        return
    
    idx = find_polygon_at_point(point)
    if idx is not None:
        state.selected_polygon_index = idx
    
    if mode == 'check_convex':
        if idx is not None:
            poly_data = state.polygons[idx]
            if isinstance(poly_data, dict):
                points = poly_data['points']
            else:
                points = poly_data
            is_conv = poly_algo.is_convex(points)
            status = "ВЫПУКЛЫЙ" if is_conv else "НЕВЫПУКЛЫЙ"
            
            from ..canvas import update_status
            update_status(f"Полигон #{idx + 1}: {status}")
        else:
            from ..canvas import update_status
            update_status("Кликните по полигону")
    
    elif mode == 'show_normals':
        if idx is not None:
            from ..canvas import redraw
            state.status_label.config(text=f"Полигон #{idx + 1}: показаны внутренние нормали")
            redraw()
        else:
            from ..canvas import update_status
            update_status("Кликните по полигону для показа нормалей")
    
    elif mode == 'convex_hull_graham':
        if idx is not None:
            poly_data = state.polygons[idx]
            if isinstance(poly_data, dict):
                points = poly_data['points']
            else:
                points = poly_data
            hull = convex_hull.graham_scan(points)
            
            hull_data = {
                'points': hull,
                'is_convex': True,
                'color': '#0066CC'
            }
            state.polygons.append(hull_data)
            from ..canvas import update_status, redraw
            update_status(f"Грэхем: построена выпуклая оболочка ({len(hull)} точек)")
            redraw()
        else:
            from ..canvas import update_status
            update_status("Кликните по полигону")
    
    elif mode == 'convex_hull_jarvis':
        if idx is not None:
            poly_data = state.polygons[idx]
            if isinstance(poly_data, dict):
                points = poly_data['points']
            else:
                points = poly_data
            hull = convex_hull.jarvis_march(points)
            hull_data = {
                'points': hull,
                'is_convex': True,
                'color': '#0066CC'
            }
            state.polygons.append(hull_data)
            
            from ..canvas import update_status, redraw
            update_status(f"Джарвис: построена выпуклая оболочка ({len(hull)} точек)")
            redraw()
        else:
            from ..canvas import update_status
            update_status("Кликните по полигону")
    
    elif mode == 'intersection':
        if idx is None:
            from ..canvas import update_status
            update_status("Кликните по полигону")
            return
        
        if state.intersection_segment is None:
            state.intersection_segment = [point, None]
            state.selected_polygon_index = idx
            from ..canvas import update_status
            update_status("Кликните вторую точку отрезка")
        else:
            state.intersection_segment[1] = point
            poly_data = state.polygons[idx]
            if isinstance(poly_data, dict):
                points = poly_data['points']
            else:
                points = poly_data
            intersects = intersection.find_intersections(state.intersection_segment, points)
            
            if intersects:
                from ..canvas import update_status
                update_status(f"Пересечение: найдено {len(intersects)} точек (жёлтые)")
            else:
                from ..canvas import update_status
                update_status("Пересечение: нет точек пересечения")
            state.intersection_segment = None
            from ..canvas import redraw
            redraw()
    
    elif mode == 'point_in_polygon':
        state.test_point = point
        found = False
        for i, poly_data in enumerate(state.polygons):
            if isinstance(poly_data, dict):
                pts = poly_data['points']
            else:
                pts = poly_data
            
            inside = point_in_polygon.point_in_polygon(point, pts)
            if inside:
                state.selected_polygon_index = i
                found = True
                from ..canvas import update_status, redraw
                update_status(f"Точка ВНУТРИ полигона #{i+1}")
                redraw()
                return
        
        if not found:
            from ..canvas import update_status, redraw
            update_status("Точка СНАРУЖИ всех полигонов")
            state.selected_polygon_index = None
            redraw()

def finish_polygon():
    if len(state.polygon_points) < 3:
        from ..canvas import update_status
        update_status("Нужно минимум 3 точки!")
        return
    
    is_conv = poly_algo.is_convex(state.polygon_points)
    poly_data = {
        'points': list(state.polygon_points),
        'is_convex': is_conv,
        'color': '#0066CC'
    }
    state.polygons.append(poly_data)
    state.polygon_points = []
    from ..canvas import update_status, redraw
    status = "Выпуклый" if is_conv else "Невыпуклый"
    update_status(f"Полигон построен: {status}")
    redraw()
