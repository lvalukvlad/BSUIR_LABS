import tkinter as tk
import state


def create():
    menubar = tk.Menu(state.root)
    state.root.config(menu=menubar)

    menubar.add_radiobutton(label="Отрезки", variable=state.lab, value=1, command=lambda: select(1))
    menubar.add_radiobutton(label="Линии 2-го порядка", variable=state.lab, value=2, command=lambda: select(2))

    menubar.add_command(label="Режим: Отрезки", state='disabled')


def select(lab):
    state.lab = lab
    from ui.toolbar import update_toolbar as update_toolbar

    label = "Отрезки" if lab == 1 else "Линии 2-го порядка"

    menubar = state.root.nametowidget(state.root.cget('menu'))
    menubar.entryconfig(3, label=f"Режим: {label}")
    update_toolbar(lab)