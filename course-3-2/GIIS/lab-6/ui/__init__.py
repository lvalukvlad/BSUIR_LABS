import tkinter as tk

import state
from ui import menu, canvas, debug_panel, toolbar


def init():
    state.root = tk.Tk()
    state.root.title("Графический редактор - Заполнение полигонов")
    state.root.geometry("1200x800")
    
    state.root.bind('<Escape>', on_escape)

    menu.create()
    toolbar.create()
    canvas.create()
    debug_panel.create()

def on_escape(event):
    if state.mode_lab == 4 and state.polygon_mode == 'build':
        if state.polygon_points:
            state.polygon_points.pop()
            state.preview_end = None
            from ui.canvas import redraw, update_status
            redraw()
            update_status(f"Точка удалена. Осталось точек: {len(state.polygon_points)}")
    elif state.mode_lab == 4 and state.polygon_mode == 'intersection':
        if state.intersection_segment:
            state.intersection_segment = None
            state.selected_polygon_index = None
            from ui.canvas import redraw, update_status
            redraw()
            update_status("Выбор отменён")
    elif state.mode_lab == 6:
        state.fill_polygon_index = None
        state.fill_seed_point = None
        state.polygon_fills = {}
        state.filled_pixels = []
        state.debug_step = 0
        state.fill_debug_steps = []
        state.debug_pixels = []
        if state.debug_list:
            state.debug_list.delete(0, tk.END)
        from ui.canvas import redraw, update_status
        redraw()
        update_status("Выбор сброшен")

def run():
    init()
    state.root.mainloop()