import tkinter as tk

import state
from ui import menu, canvas, debug_panel, toolbar


def init():
    state.root = tk.Tk()
    state.root.title("Графический редактор отрезков")
    state.root.geometry("1200x800")
    
    state.root.bind('<Escape>', on_escape)

    menu.create()
    toolbar.create()
    canvas.create()
    debug_panel.create()

def on_escape(event):
    if state.lab == 4 and state.polygon_mode == 'build':
        if state.polygon_points:
            state.polygon_points.pop()
            state.preview_end = None
            from ui.canvas import redraw, update_status
            redraw()
            update_status(f"Точка удалена. Осталось точек: {len(state.polygon_points)}")
    elif state.lab == 4 and state.polygon_mode == 'intersection':
        if state.intersection_segment:
            state.intersection_segment = None
            state.selected_polygon_index = None
            from ui.canvas import redraw, update_status
            redraw()
            update_status("Выбор отменён")

def run():
    init()
    state.root.mainloop()