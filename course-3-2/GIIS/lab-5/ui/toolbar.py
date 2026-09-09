from tkinter import ttk
import state

import algorithms.lab_1.dda as dda
import algorithms.lab_1.bresenham as bresenham
import algorithms.lab_1.wu as wu

import algorithms.lab_2.circle as circle
import algorithms.lab_2.ellipse as ellipse
import algorithms.lab_2.parabola as parabola
import algorithms.lab_2.hyperbola as hyperbola

import algorithms.lab_3.hermite as hermite
import algorithms.lab_3.bezier as bezier
import algorithms.lab_3.bspline as bspline


def create():
    if hasattr(state, 'toolbar') and state.toolbar:
        state.toolbar.destroy()

    toolbar = ttk.Frame(state.root, relief='raised', borderwidth=1)
    toolbar.pack(side='top', fill='x', padx=2, pady=2)
    state.toolbar = toolbar

    ttk.Label(toolbar, text="Алгоритм:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)
    toolbar_mini = ttk.Frame(state.toolbar, relief='raised', borderwidth=1)
    toolbar_mini.pack(side='left', fill='x', padx=2, pady=2)
    state.toolbar_mini = toolbar_mini

    ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10)

    state.mode_btn = ttk.Button(toolbar, text="Режим: Обычный", command=toggle_mode)
    state.mode_btn.pack(side='left', padx=5)

    ttk.Button(toolbar, text="Очистить", command=clear).pack(side='left', padx=5)

    state.status_label = ttk.Label(toolbar, text="Выберите алгоритм")
    state.status_label.pack(side='right', padx=10)


def update_toolbar(lab: int):
    if lab == 4:
        state.mode_btn.pack_forget()
    else:
        state.mode_btn.pack(side='left', padx=5)
    
    for widget in state.toolbar_mini.winfo_children():
        widget.destroy()
    
    if lab == 1:
        ttk.Button(state.toolbar_mini, text=dda.name, command=lambda: select(dda)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=bresenham.name, command=lambda: select(bresenham)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=wu.name, command=lambda: select(wu)).pack(side='left', padx=2)
    elif lab == 2:
        ttk.Button(state.toolbar_mini, text=circle.name, command=lambda: select(circle)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=ellipse.name, command=lambda: select(ellipse)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=parabola.name, command=lambda: select(parabola)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=hyperbola.name, command=lambda: select(hyperbola)).pack(side='left', padx=2)
    elif lab == 3:
        ttk.Button(state.toolbar_mini, text=hermite.name, command=lambda: select(hermite)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=bezier.name, command=lambda: select(bezier)).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text=bspline.name, command=lambda: select(bspline)).pack(side='left', padx=2)
        
        ttk.Separator(state.toolbar_mini, orient='vertical').pack(side='left', fill='y', padx=10)
        
        state.adjust_btn = ttk.Button(state.toolbar_mini, text="Корректировка", command=toggle_adjustment)
        state.adjust_btn.pack(side='left', padx=2)
        
        ttk.Button(state.toolbar_mini, text="Очистить точки", command=clear_lab3_points).pack(side='left', padx=2)
    elif lab == 4:
        ttk.Button(state.toolbar_mini, text="Построить", command=lambda: set_polygon_mode('build')).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text="Завершить", command=finish_polygon).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text="Выпуклость", command=lambda: set_polygon_mode('check_convex')).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text="Нормали", command=lambda: set_polygon_mode('show_normals')).pack(side='left', padx=2)
        
        ttk.Separator(state.toolbar_mini, orient='vertical').pack(side='left', fill='y', padx=10)
        
        ttk.Button(state.toolbar_mini, text="Грэхем", command=lambda: set_polygon_mode('convex_hull_graham')).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text="Джарвис", command=lambda: set_polygon_mode('convex_hull_jarvis')).pack(side='left', padx=2)
        
        ttk.Separator(state.toolbar_mini, orient='vertical').pack(side='left', fill='y', padx=10)
        
        ttk.Button(state.toolbar_mini, text="Пересечение", command=lambda: set_polygon_mode('intersection')).pack(side='left', padx=2)
        ttk.Button(state.toolbar_mini, text="Точка вн/снар", command=lambda: set_polygon_mode('point_in_polygon')).pack(side='left', padx=2)
        
        ttk.Separator(state.toolbar_mini, orient='vertical').pack(side='left', fill='y', padx=10)
        
        ttk.Button(state.toolbar_mini, text="Очистить полигоны", command=clear_polygons).pack(side='left', padx=2)


def set_polygon_mode(mode):
    state.polygon_mode = mode
    mode_names = {
        'build': 'Кликами стройте полигон, затем нажмите Завершить',
        'check_convex': 'Кликните по полигону - узнаете выпуклый ли он',
        'show_normals': 'Кликните по полигону - увидите нормали',
        'convex_hull_graham': 'Кликните по полигону - построится выпуклая оболочка',
        'convex_hull_jarvis': 'Кликните по полигону - построится выпуклая оболочка',
        'intersection': 'Кликните по полигону, затем задайте отрезок',
        'point_in_polygon': 'Кликните по полигону, затем кликните точку'
    }
    state.status_label.config(text=f"Режим: {mode_names.get(mode, mode)}")
    state.intersection_segment = None
    state.test_point = None


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


def toggle_adjustment():
    state.adjustment_mode = not state.adjustment_mode
    if state.adjustment_mode:
        state.adjust_btn.config(text="Корректировка: ВКЛ")
        state.status_label.config(text="Режим корректировки: кликните по точке для перемещения")
    else:
        state.adjust_btn.config(text="Корректировка")
        state.status_label.config(text="Режим корректировки: ВЫКЛ")


def clear_lab3_points():
    state.lab_3_points = []
    from ui.canvas import redraw
    redraw()


def clear_polygons():
    state.polygon_points = []
    state.polygons = []
    state.intersection_segment = None
    state.test_point = None
    from ui.canvas import redraw
    redraw()


def finish_polygon():
    from ui.lab_5.canvas_5 import finish_polygon as fp
    fp()


def clear():
    state.all_pixels = []
    state.lab_3_points = []
    state.polygon_points = []
    state.polygons = []
    state.intersection_segment = None
    state.test_point = None
    from ui.canvas import clear_selection, redraw
    clear_selection()
    redraw()


def update_status(text):
    state.status_label.config(text=text)
