import tkinter as tk

import state
from ui import menu, toolbar, canvas, debug_panel


def init():
    state.root = tk.Tk()
    state.root.title("Графический редактор отрезков")
    state.root.geometry("1200x800")

    menu.create()
    toolbar.create()
    canvas.create()
    debug_panel.create()

def run():
    init()
    state.root.mainloop()