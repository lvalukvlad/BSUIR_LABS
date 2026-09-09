import tkinter as tk
import state
import algorithms.transformations as transforms


def create():
    state.canvas = tk.Canvas(
        state.root,
        bg='#FAFAFA',
        highlightthickness=1,
        highlightbackground='gray'
    )
    state.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)


Z_PROJECTION = 0.5


def grid_to_screen(x, y, z=0):
    w = state.canvas.winfo_width() or 800
    h = state.canvas.winfo_height() or 600
    cx, cy = w // 2, h // 2
    
    if state.use_perspective:
        x, y, z = transforms.apply_perspective((x, y, z), state.perspective_d)
    
    scale = state.CELL_SIZE
    
    x_proj = x - z * Z_PROJECTION
    y_proj = y - z * Z_PROJECTION
    
    sx = cx + x_proj * scale
    sy = cy - y_proj * scale
    return sx, sy, z


def transform_vertex(v):
    return transforms.apply_transform(v, state.transform_matrix)


def redraw():
    c = state.canvas
    c.delete('all')
    
    w = c.winfo_width() or 800
    h = c.winfo_height() or 600
    
    draw_grid(c, w, h)
    draw_3d_axes(c, w, h)
    draw_legend(c, w, h)
    
    if not state.vertices:
        draw_placeholder(c, w, h)
        return
    
    transformed_vertices = [transform_vertex(v) for v in state.vertices]
    
    max_z = -float('inf')
    min_z = float('inf')
    for v in transformed_vertices:
        max_z = max(max_z, v[2])
        min_z = min(min_z, v[2])
    z_range = max_z - min_z if max_z != min_z else 1
    
    edges_with_depth = []
    for edge in state.edges:
        if len(edge) >= 2:
            i1, i2 = edge[0], edge[1]
            if i1 < len(transformed_vertices) and i2 < len(transformed_vertices):
                v1 = transformed_vertices[i1]
                v2 = transformed_vertices[i2]
                avg_z = (v1[2] + v2[2]) / 2
                edges_with_depth.append((avg_z, i1, i2, v1, v2))
    
    edges_with_depth.sort(key=lambda x: x[0], reverse=True)
    
    for avg_z, i1, i2, v1, v2 in edges_with_depth:
        x1, y1, z1 = grid_to_screen(v1[0], v1[1], v1[2])
        x2, y2, z2 = grid_to_screen(v2[0], v2[1], v2[2])
        
        depth_factor = 1.0 - (avg_z - min_z) / z_range * 0.5
        gray = int(180 * depth_factor + 50)
        color = f'#{gray:02x}{gray:02x}{gray:02x}'
        
        c.create_line(x1, y1, x2, y2, fill=color, width=2)
    
    sorted_vertices = sorted(enumerate(transformed_vertices), key=lambda x: x[1][2], reverse=True)
    
    for i, v in sorted_vertices:
        sx, sy, vz = grid_to_screen(v[0], v[1], v[2])
        
        depth_factor = 1.0 - (v[2] - min_z) / z_range * 0.4
        r = int(0 * depth_factor + 150)
        g = int(102 * depth_factor + 50)
        b = int(204 * depth_factor + 50)
        color = f'#{r:02x}{g:02x}{b:02x}'
        
        size = state.CELL_SIZE * 2
        c.create_oval(sx-size/2, sy-size/2, sx+size/2, sy+size/2, 
                      fill=color, outline='#333333', width=1)


def draw_grid(c, w, h):
    cx, cy = w // 2, h // 2
    grid_color = '#E8E8E8'
    
    for x in range(0, w, state.CELL_SIZE * 5):
        c.create_line(x, 0, x, h, fill=grid_color)
    for y in range(0, h, state.CELL_SIZE * 5):
        c.create_line(0, y, w, y, fill=grid_color)
    
    c.create_line(0, cy, w, cy, fill='#BBBBBB', width=1)
    c.create_line(cx, 0, cx, h, fill='#BBBBBB', width=1)


def draw_3d_axes(c, w, h):
    cx, cy = w // 2, h // 2
    
    ax = 80
    ay = 80
    az = 80
    
    x1, y1, _ = grid_to_screen(0, 0, 0)
    x2, y2, _ = grid_to_screen(ax, 0, 0)
    x3, y3, _ = grid_to_screen(0, ay, 0)
    x4, y4, _ = grid_to_screen(0, 0, az)
    
    c.create_line(x1, y1, x2, y2, fill='#FF4444', width=3)
    c.create_line(x1, y1, x3, y3, fill='#44AA44', width=3)
    c.create_line(x1, y1, x4, y4, fill='#4444FF', width=3)
    
    c.create_polygon(
        x2, y2, x2-8, y2-4, x2-8, y2+4,
        fill='#FF4444', outline='#FF4444'
    )
    c.create_polygon(
        x3, y3, x3-4, y3+8, x3+4, y3+8,
        fill='#44AA44', outline='#44AA44'
    )
    c.create_polygon(
        x4, y4, x4-6, y4-2, x4-2, y4-8, x4+6, y4+2,
        fill='#4444FF', outline='#4444FF'
    )
    
    c.create_text(x2 + 10, y2, text='X', fill='#FF4444', font=('Arial', 12, 'bold'), anchor=tk.W)
    c.create_text(x3 + 15, y3, text='Y', fill='#44AA44', font=('Arial', 12, 'bold'), anchor=tk.W)
    c.create_text(x4 + 10, y4 - 5, text='Z', fill='#4444FF', font=('Arial', 12, 'bold'), anchor=tk.W)


def draw_legend(c, w, h):
    legend_x = 10
    legend_y = 10
    
    c.create_rectangle(legend_x, legend_y, legend_x + 120, legend_y + 60, 
                       fill='white', outline='#CCCCCC', width=1)
    
    c.create_oval(legend_x + 10, legend_y + 15, legend_x + 20, legend_y + 25, fill='#FF4444')
    c.create_text(legend_x + 25, legend_y + 20, text='X', font=('Arial', 9))
    
    c.create_oval(legend_x + 10, legend_y + 32, legend_x + 20, legend_y + 42, fill='#44AA44')
    c.create_text(legend_x + 25, legend_y + 37, text='Y', font=('Arial', 9))
    
    c.create_oval(legend_x + 10, legend_y + 49, legend_x + 20, legend_y + 59, fill='#4444FF')
    c.create_text(legend_x + 25, legend_y + 54, text='Z', font=('Arial', 9))


def draw_placeholder(c, w, h):
    cx, cy = w // 2, h // 2
    c.create_text(cx, cy, text='Загрузите 3D объект:\nФайл → Загрузить пример\nили нажмите клавиши',
                  font=('Arial', 14), fill='#888888', justify=tk.CENTER)


def update_status(text):
    if state.status_label:
        state.status_label.config(text=text)
