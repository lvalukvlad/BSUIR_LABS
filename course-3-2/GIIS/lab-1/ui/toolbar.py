from tkinter import ttk
import state

import algorithms.dda as dda
import algorithms.bresenham as bresenham
import algorithms.wu as wu


def create():
    toolbar = ttk.Frame(state.root, relief='raised', borderwidth=1)
    toolbar.pack(side='top', fill='x', padx=2, pady=2)

    ttk.Label(toolbar, text="Алгоритм:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)

    ttk.Button(toolbar, text=dda.name, command=lambda: select(dda)).pack(side='left', padx=2)
    ttk.Button(toolbar, text=bresenham.name, command=lambda: select(bresenham)).pack(side='left', padx=2)
    ttk.Button(toolbar, text=wu.name, command=lambda: select(wu)).pack(side='left', padx=2)

    ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)

    state.mode_btn = ttk.Button(toolbar, text="Режим: Обычный", command=toggle_mode)
    state.mode_btn.pack(side='left', padx=5)

    ttk.Button(toolbar, text="Очистить", command=clear).pack(side='left', padx=5)

    state.status_label = ttk.Label(toolbar, text="Выберите алгоритм")
    state.status_label.pack(side='right', padx=10)


def select(algorithm_module):
    state.current_algorithm = algorithm_module.generate
    state.algorithm_name = algorithm_module.name
    state.status_label.config(text=f"Выбран: {algorithm_module.name}")


def toggle_mode():
    if state.mode == "normal":
        state.mode = "debug"
        state.mode_btn.config(text="Режим: Отладочный")
        state.debug_frame.pack(side='right', fill='y', padx=5)
        from ui.debug_panel import reset
        reset()
        state.status_label.config(text="Отладка: установите точки")
    else:
        state.mode = "normal"
        state.mode_btn.config(text="Режим: Обычный")
        state.debug_frame.pack_forget()
        from ui.debug_panel import reset
        reset()
        state.status_label.config(text="Обычный режим")

    from ui.canvas import redraw
    redraw()


def clear():
    state.all_pixels = []
    from ui.canvas import clear_selection, redraw
    clear_selection()
    redraw()


def update_status(text):
    state.status_label.config(text=text)