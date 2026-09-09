import tkinter as tk
import state


def create():
    state.lab = tk.IntVar(value=1)
    
    menubar = tk.Menu(state.root)
    state.root.config(menu=menubar)

    menubar.add_radiobutton(label="Отрезки", variable=state.lab, value=1, command=lambda: select(1))
    menubar.add_radiobutton(label="Линии 2-го порядка", variable=state.lab, value=2, command=lambda: select(2))
    menubar.add_radiobutton(label="Кривые", variable=state.lab, value=3, command=lambda: select(3))
    menubar.add_radiobutton(label="Построение полигонов", variable=state.lab, value=4, command=lambda: select(4))


def select(lab):
    from ui.toolbar import update_toolbar as update_toolbar
    
    if state.lab == 4 and lab != 4 and state.polygons:
        from algorithms.lab_1.dda import Point, Pixel
        from algorithms.lab_5.polygon import build_polygon
        for poly_data in state.polygons:
            if isinstance(poly_data, dict):
                points = poly_data['points']
            else:
                points = poly_data
            pixels = build_polygon(points)
            for p in pixels:
                pt = Point(int(p[0]), int(p[1]))
                pixel = Pixel(pt, p[2])
                state.all_pixels.append(pixel)
    
    state.lab = lab

    labels = {1: "Отрезки", 2: "Линии 2-го порядка", 3: "Кривые", 4: "Построение полигонов"}
    label = labels.get(lab, "Отрезки")

    menubar = state.root.nametowidget(state.root.cget('menu'))
    menubar.entryconfig(4, label=f"Режим: {label}")
    update_toolbar(lab)
    
    from ui.canvas import redraw
    redraw()
