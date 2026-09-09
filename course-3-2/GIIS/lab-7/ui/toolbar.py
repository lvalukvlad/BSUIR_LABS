import tkinter as tk
from tkinter import ttk
import state


def create():
    toolbar = ttk.Frame(state.root, relief='raised', borderwidth=1)
    toolbar.pack(side='top', fill='x', padx=2, pady=2)
    state.toolbar = toolbar
    
    ttk.Label(toolbar, text="Режим:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)
    
    ttk.Button(toolbar, text="Делоне", command=lambda: set_mode('delaunay')).pack(side='left', padx=2)
    ttk.Button(toolbar, text="Вороной", command=lambda: set_mode('voronoi')).pack(side='left', padx=2)
    
    ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
    
    ttk.Button(toolbar, text="Построить", command=build).pack(side='left', padx=2)
    ttk.Button(toolbar, text="Шаг >>", command=step_forward).pack(side='left', padx=2)
    ttk.Button(toolbar, text="Сброс", command=reset_debug).pack(side='left', padx=2)
    
    ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
    
    ttk.Button(toolbar, text="Очистить", command=clear).pack(side='left', padx=2)
    ttk.Button(toolbar, text="Случайные", command=add_random).pack(side='left', padx=2)
    
    ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)
    
    ttk.Button(toolbar, text="Отладка", command=toggle_debug).pack(side='left', padx=2)
    
    state.status_label = ttk.Label(toolbar, text="Кликните на холсте для добавления точек")
    state.status_label.pack(side='right', padx=10)
    
    state.debug_frame = tk.Frame(state.root, relief='raised', borderwidth=1)
    
    tk.Label(state.debug_frame, text="Отладка", font=('Arial', 10, 'bold')).pack(pady=5)
    
    scrollbar = tk.Scrollbar(state.debug_frame)
    scrollbar.pack(side='right', fill='y')
    
    state.debug_list = tk.Listbox(state.debug_frame, yscrollcommand=scrollbar.set, height=25, width=45)
    state.debug_list.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=state.debug_list.yview)


def set_mode(m):
    state.voronoi_mode = m
    mode_names = {'delaunay': 'Триангуляция Делоне', 'voronoi': 'Диаграмма Вороного'}
    state.status_label.config(text=f"Режим: {mode_names[m]}")


def toggle_debug():
    if state.mode == "normal":
        state.mode = "debug"
        state.debug_frame.pack(side='right', fill='y', padx=5)
        state.status_label.config(text="Режим отладки")
    else:
        state.mode = "normal"
        state.debug_frame.pack_forget()
        state.status_label.config(text="Обычный режим")


def build():
    from algorithms import delaunay, voronoi
    
    if len(state.points) < 3:
        state.status_label.config(text="Нужно минимум 3 точки!")
        return
    
    if state.voronoi_mode == 'delaunay':
        if state.mode == "debug":
            state.triangles = delaunay.delaunay_debug(state.points)
            state.delaunay_debug_steps = delaunay.debug_steps
            state.delaunay_debug_step = 0
        else:
            state.triangles = delaunay.delaunay(state.points)
        state.voronoi_edges = []
        state.voronoi_vertices = []
        state.status_label.config(text=f"Триангуляция Делоне: {len(state.triangles)} треугольников")
    else:
        tris = delaunay.delaunay(state.points)
        state.triangles = tris
        if state.mode == "debug":
            edges, vertices = voronoi.voronoi_debug(state.points, tris)
            state.voronoi_edges = edges
            state.voronoi_vertices = vertices
            state.voronoi_debug_steps = voronoi.debug_steps
            state.voronoi_debug_step = 0
        else:
            edges, vertices = voronoi.voronoi(state.points, tris)
            state.voronoi_edges = edges
            state.voronoi_vertices = vertices
        state.status_label.config(text=f"Диаграмма Вороного: {len(state.voronoi_edges)} рёбер")
    
    update_debug_list()
    from ui.canvas import redraw
    redraw()


def step_forward():
    if state.voronoi_mode == 'delaunay' and state.delaunay_debug_steps:
        if state.delaunay_debug_step < len(state.delaunay_debug_steps):
            step = state.delaunay_debug_steps[state.delaunay_debug_step]
            state.delaunay_debug_step += 1
            state.status_label.config(text=f"Шаг {state.delaunay_debug_step}: {step['description']}")
            update_debug_list()
            from ui.canvas import redraw
            redraw()
        else:
            state.status_label.config(text="Отладка завершена!")
    elif state.voronoi_mode == 'voronoi' and state.voronoi_debug_steps:
        if state.voronoi_debug_step < len(state.voronoi_debug_steps):
            step = state.voronoi_debug_steps[state.voronoi_debug_step]
            state.voronoi_debug_step += 1
            state.status_label.config(text=f"Шаг {state.voronoi_debug_step}: {step['description']}")
            update_debug_list()
            from ui.canvas import redraw
            redraw()
        else:
            state.status_label.config(text="Отладка завершена!")


def reset_debug():
    state.delaunay_debug_step = 0
    state.voronoi_debug_step = 0
    if state.debug_list:
        state.debug_list.delete(0, tk.END)
    state.status_label.config(text="Отладка сброшена")
    from ui.canvas import redraw
    redraw()


def clear():
    state.points = []
    state.triangles = []
    state.voronoi_edges = []
    state.voronoi_vertices = []
    state.delaunay_debug_steps = []
    state.delaunay_debug_step = 0
    state.voronoi_debug_steps = []
    state.voronoi_debug_step = 0
    if state.debug_list:
        state.debug_list.delete(0, tk.END)
    state.status_label.config(text="Очищено")
    from ui.canvas import redraw
    redraw()


def add_random():
    import random
    from ui.canvas import screen_to_grid
    w = state.canvas.winfo_width()
    h = state.canvas.winfo_height()
    margin_px = 20
    for _ in range(8):
        sx = random.randint(margin_px, w - margin_px)
        sy = random.randint(margin_px, h - margin_px)
        gx, gy = screen_to_grid(sx, sy)
        state.points.append((gx, gy))
    state.status_label.config(text=f"Добавлено 8 случайных точек. Всего: {len(state.points)}")
    from ui.canvas import redraw
    redraw()


def update_debug_list():
    if not state.debug_list:
        return
    state.debug_list.delete(0, tk.END)
    
    if state.voronoi_mode == 'delaunay' and state.delaunay_debug_steps:
        for i, step in enumerate(state.delaunay_debug_steps[:state.delaunay_debug_step]):
            state.debug_list.insert(tk.END, f"{i+1}. {step['description']}")
    elif state.voronoi_mode == 'voronoi' and state.voronoi_debug_steps:
        for i, step in enumerate(state.voronoi_debug_steps[:state.voronoi_debug_step]):
            state.debug_list.insert(tk.END, f"{i+1}. {step['description']}")
