import tkinter as tk
from tkinter import ttk
import state


def create():
    state.debug_frame = ttk.Frame(state.root, width=250)

    ttk.Label(state.debug_frame, text="Отладка", font=('Arial', 12, 'bold')).pack(pady=10)

    btn_frame = ttk.Frame(state.debug_frame)
    btn_frame.pack(pady=5)

    ttk.Button(btn_frame, text="Шаг ->", command=step).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Авто", command=auto).pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Сброс", command=reset).pack(side=tk.LEFT, padx=2)

    state.debug_info = ttk.Label(state.debug_frame, text="Ожидание...", justify=tk.LEFT)
    state.debug_info.pack(pady=10, padx=5, anchor='w')

    state.debug_list = tk.Listbox(state.debug_frame, height=25)
    state.debug_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


def step():
    if state.debug_generator is None:
        return

    try:
        pixel = next(state.debug_generator)
        state.debug_pixels.append(pixel)
        state.debug_step += 1
        state.debug_list.insert(tk.END,
                                f"{state.debug_step}: ({pixel.point.x}, {pixel.point.y}) I={pixel.intensity:.2f}")
        state.debug_list.see(tk.END)
        state.debug_info.config(
            text=f"Шаг: {state.debug_step}\n"
                 f"Текущий: ({pixel.point.x}, {pixel.point.y})\n"
                 f"Интенсивность: {pixel.intensity:.2f}"
        )

        from ui.canvas import redraw
        redraw()
    except StopIteration:
        state.debug_info.config(text="Готово!")
        state.debug_generator = None


def auto():
    def next_step():
        if state.debug_generator:
            step()
            if state.debug_generator:
                state.root.after(100, next_step)

    next_step()


def reset():
    state.debug_pixels = []
    state.debug_step = 0
    state.debug_generator = None
    state.start_point = None
    state.end_point = None
    if state.debug_list:
        state.debug_list.delete(0, tk.END)
    if state.debug_info:
        state.debug_info.config(text="Ожидание...")

    from ui.canvas import redraw, clear_selection
    clear_selection()
    redraw()