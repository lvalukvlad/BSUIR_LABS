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
    if state.mode_lab == 6 and state.fill_debug_steps:
        fill_step()
        return
    
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
    if state.mode_lab == 6 and state.fill_debug_steps:
        fill_auto()
        return
    
    def next_step():
        if state.debug_generator:
            step()
            if state.debug_generator:
                state.root.after(100, next_step)

    next_step()


def reset():
    if state.mode_lab == 6:
        reset_fill_debug()
        return
    
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


def reset_fill_debug():
    state.debug_pixels = []
    state.debug_step = 0
    if state.debug_list:
        state.debug_list.delete(0, tk.END)
    if state.debug_info:
        state.debug_info.config(text="Ожидание...")

    if state.mode_lab == 6 and state.fill_debug_steps:
        show_fill_step(0)


def show_fill_step(step_index):
    if not state.fill_debug_steps or step_index >= len(state.fill_debug_steps):
        if state.debug_info:
            state.debug_info.config(text="Заполнение завершено")
        return

    step_data = state.fill_debug_steps[step_index]
    
    if 'y' in step_data:
        info_text = f"Строка y={step_data['y']}\n"
        if 'intersections' in step_data:
            info_text += f"Пересечения: {step_data['intersections']}\n"
        if 'intervals' in step_data:
            info_text += f"Интервалы: {step_data['intervals']}\n"
        if 'aet_before' in step_data:
            info_text += f"АР до: {step_data['aet_before']}\n"
        if 'aet_after' in step_data:
            info_text += f"АР после: {step_data['aet_after']}\n"
    elif 'current' in step_data:
        info_text = f"Шаг {step_data['step']}\n"
        info_text += f"Текущий: {step_data['current']}\n"
        if 'filled' in step_data:
            info_text += f"Заполнено: {step_data['filled']}\n"
        if 'neighbors' in step_data:
            info_text += f"Соседи: {step_data['neighbors']}\n"
        if 'interval' in step_data:
            info_text += f"Интервал: {step_data['interval']}\n"
        if 'new_seeds' in step_data:
            info_text += f"Новые затравки: {step_data['new_seeds']}\n"
        info_text += f"Размер стека: {step_data.get('stack_size', 0)}"
    
    if state.debug_info:
        state.debug_info.config(text=info_text)

    state.debug_pixels = []
    for i in range(step_index + 1):
        step = state.fill_debug_steps[i]
        if 'pixels' in step:
            for p in step['pixels']:
                if isinstance(p, list):
                    for px in p:
                        state.debug_pixels.append((px[0], px[1], 1.0))
                else:
                    state.debug_pixels.append((p[0], p[1], 1.0))
        elif 'filled' in step:
            for p in step['filled']:
                state.debug_pixels.append((p[0], p[1], 1.0))
        elif 'interval' in step:
            x1, x2 = step['interval']
            y = step['current'][1]
            for x in range(x1, x2 + 1):
                state.debug_pixels.append((x, y, 1.0))
    
    if state.debug_list:
        state.debug_list.delete(0, tk.END)
        state.debug_list.insert(tk.END, f"Шаг {step_index + 1}/{len(state.fill_debug_steps)}")
    
    from ui.canvas import redraw
    redraw()


def fill_step():
    if not state.fill_debug_steps:
        return
    
    next_step = state.debug_step + 1
    if next_step >= len(state.fill_debug_steps):
        if state.debug_info:
            state.debug_info.config(text="Заполнение завершено")
        return
    
    state.debug_step = next_step
    show_fill_step(state.debug_step)


def fill_auto():
    def next_step():
        if state.debug_step < len(state.fill_debug_steps) - 1:
            fill_step()
            state.root.after(100, next_step)
        else:
            if state.debug_info:
                state.debug_info.config(text="Заполнение завершено")

    next_step()