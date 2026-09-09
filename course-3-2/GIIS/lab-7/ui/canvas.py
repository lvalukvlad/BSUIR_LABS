import tkinter as tk
import state

_redraw_pending = False


def create():
    state.canvas = tk.Canvas(
        state.root,
        bg='white',
        highlightthickness=1,
        highlightbackground='gray'
    )
    state.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    state.canvas.bind('<Configure>', lambda e: redraw())
    state.canvas.bind('<Button-1>', on_click)
    state.canvas.bind('<Motion>', on_move)


def screen_to_grid(sx, sy):
    w = state.canvas.winfo_width()
    h = state.canvas.winfo_height()
    offset_x = (w // 2) % 10
    offset_y = (h // 2) % 10
    gx = (sx - offset_x) // 10
    gy = (sy - offset_y) // 10
    return (gx, gy)


def grid_to_screen(gx, gy):
    w = state.canvas.winfo_width()
    h = state.canvas.winfo_height()
    offset_x = (w // 2) % 10
    offset_y = (h // 2) % 10
    sx = offset_x + gx * 10
    sy = offset_y + gy * 10
    return (sx, sy)


def on_click(event):
    gx, gy = screen_to_grid(event.x, event.y)
    state.points.append((gx, gy))
    state.status_label.config(text=f"Точек: {len(state.points)}")
    redraw()


def on_move(event):
    global _redraw_pending
    state.preview_point = screen_to_grid(event.x, event.y)
    if not _redraw_pending:
        _redraw_pending = True
        state.canvas.after(30, _do_preview_redraw)


def _do_preview_redraw():
    global _redraw_pending
    _redraw_pending = False
    redraw()


def draw_grid():
    w = state.canvas.winfo_width()
    h = state.canvas.winfo_height()
    offset_x = (w // 2) % 10
    offset_y = (h // 2) % 10
    
    for x in range(offset_x, w, 10):
        state.canvas.create_line(x, 0, x, h, fill='#E8E8E8')
    for y in range(offset_y, h, 10):
        state.canvas.create_line(0, y, w, y, fill='#E8E8E8')
    
    cx, cy = w // 2, h // 2
    state.canvas.create_line(cx, 0, cx, h, fill='#CCCCCC', width=2)
    state.canvas.create_line(0, cy, w, cy, fill='#CCCCCC', width=2)


def draw_points():
    for p in state.points:
        sx, sy = grid_to_screen(p[0], p[1])
        state.canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, fill='#CC0000', outline='#880000', width=2)


def draw_preview():
    if state.preview_point:
        sx, sy = grid_to_screen(state.preview_point[0], state.preview_point[1])
        state.canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, outline='#888888', dash=(3, 3))


def draw_triangles():
    to_draw = []
    
    if state.voronoi_mode == 'delaunay':
        if state.mode == "debug" and state.delaunay_debug_steps and state.delaunay_debug_step > 0:
            step_idx = min(state.delaunay_debug_step - 1, len(state.delaunay_debug_steps) - 1)
            to_draw = state.delaunay_debug_steps[step_idx].get('triangles', [])
        else:
            to_draw = state.triangles
        
        for t in to_draw:
            for i in range(3):
                p1, p2 = t[i], t[(i + 1) % 3]
                sx1, sy1 = grid_to_screen(p1[0], p1[1])
                sx2, sy2 = grid_to_screen(p2[0], p2[1])
                state.canvas.create_line(sx1, sy1, sx2, sy2, fill='#0066CC', width=2)


def draw_voronoi():
    if state.voronoi_mode != 'voronoi':
        return
    
    edges_to_draw = []
    vertices_to_draw = []
    
    if state.mode == "debug" and state.voronoi_debug_steps and state.voronoi_debug_step > 0:
        step_idx = min(state.voronoi_debug_step - 1, len(state.voronoi_debug_steps) - 1)
        step = state.voronoi_debug_steps[step_idx]
        edges_to_draw = step.get('edges', [])
        vertices_to_draw = step.get('vertices', [])
    else:
        edges_to_draw = state.voronoi_edges
        vertices_to_draw = state.voronoi_vertices
    
    for e in edges_to_draw:
        try:
            sx1, sy1 = grid_to_screen(int(e[0][0]), int(e[0][1]))
            sx2, sy2 = grid_to_screen(int(e[1][0]), int(e[1][1]))
            state.canvas.create_line(sx1, sy1, sx2, sy2, fill='#FF6600', width=2, dash=(5, 3))
        except (ValueError, TypeError, IndexError):
            pass

    for v in vertices_to_draw:
        try:
            sx, sy = grid_to_screen(int(v[0]), int(v[1]))
            state.canvas.create_oval(sx - 4, sy - 4, sx + 4, sy + 4, fill='#FF6600', outline='')
        except (ValueError, TypeError, IndexError):
            pass


def redraw():
    state.canvas.delete('all')
    draw_grid()
    draw_triangles()
    draw_voronoi()
    draw_points()
    draw_preview()
