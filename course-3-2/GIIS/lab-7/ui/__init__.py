import tkinter as tk
import state
from ui import canvas, toolbar


def init():
    state.root = tk.Tk()
    state.root.title("Триангуляция Делоне и Диаграмма Вороного")
    state.root.geometry("1200x700")
    
    state.root.bind('<Escape>', on_escape)
    
    toolbar.create()
    canvas.create()


def on_escape(event):
    if state.points:
        state.points.pop()
        state.preview_point = None
        from ui.canvas import redraw
        redraw()


def run():
    init()
    state.root.mainloop()
