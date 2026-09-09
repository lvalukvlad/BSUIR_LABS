import tkinter as tk
import state

import algorithms.dda as dda
import algorithms.bresenham as bresenham
import algorithms.wu as wu


def create():
    menubar = tk.Menu(state.root)
    state.root.config(menu=menubar)

    line_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Отрезки", menu=line_menu)

    line_menu.add_command(label=dda.name, command=lambda: select(dda))
    line_menu.add_command(label=bresenham.name, command=lambda: select(bresenham))
    line_menu.add_command(label=wu.name, command=lambda: select(wu))

def select(algorithm_module):
    state.current_algorithm = algorithm_module.generate
    state.algorithm_name = algorithm_module.name
    from ui.toolbar import update_status
    update_status(f"Выбран: {algorithm_module.name}")