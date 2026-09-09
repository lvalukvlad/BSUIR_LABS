import tkinter as tk
import state
import math
from ui.debug_panel import step
from ui.lab_2.canvas_2 import draw_shape_preview, handle_shape_click
from ui.lab_1.canvas_1 import draw_line_preview, handle_line_click

def create():
    state.canvas = tk.Canvas(
        state.root,
        bg='white',
        highlightthickness=1,
        highlightbackground='gray'
    )
    state.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    state.canvas.bind('<Configure>', lambda e: redraw())
    state.canvas.bind('<Button-1>', on_click)
    state.canvas.bind('<Motion>', on_move)

def clear_selection():
    state.start_point = None
    state.end_point = None
    state.debug_generator = None
    state.debug_pixels = []
    state.debug_step = 0
    if state.debug_list:
        state.debug_list.delete(0, tk.END)


def draw_preview():
    if state.mode == "debug":
        return
    if not state.start_point or not hasattr(state, 'preview_end'):
        return

    if state.lab == 1:
        draw_line_preview()
    else:
        draw_shape_preview()

def screen_to_grid(sx, sy):
    w = state.canvas.winfo_width()
    h = state.canvas.winfo_height()
    offset_x = (w // 2) % state.CELL_SIZE
    offset_y = (h // 2) % state.CELL_SIZE

    gx = (sx - offset_x) // state.CELL_SIZE
    gy = (sy - offset_y) // state.CELL_SIZE
    return (gx, gy)


def grid_to_screen(gx, gy):
    w = state.canvas.winfo_width()
    h = state.canvas.winfo_height()
    offset_x = (w // 2) % state.CELL_SIZE
    offset_y = (h // 2) % state.CELL_SIZE

    sx = offset_x + gx * state.CELL_SIZE
    sy = offset_y + gy * state.CELL_SIZE
    return (sx, sy)


def on_click(event):
    if state.current_algorithm is None:
        update_status("Сначала выберите алгоритм!")
        return
    point = screen_to_grid(event.x, event.y)
    if state.lab == 1:
        handle_line_click(point)
    else:
        handle_shape_click(point)

def on_move(event):
    if state.start_point and state.end_point is None and state.mode == "normal":
        state.preview_end = screen_to_grid(event.x, event.y)
        redraw()


def redraw():

    c = state.canvas
    c.delete('all')

    w = c.winfo_width()
    h = c.winfo_height()

    draw_grid(c, w, h)

    draw_axes(c, w, h)

    for pixel in state.all_pixels:
        draw_pixel(pixel, '#0066CC')

    for pixel in state.debug_pixels:
        draw_pixel(pixel, '#FF4444', highlight=True)

    if hasattr(state, 'preview_end') and state.start_point and state.end_point is None:
        draw_preview()


def draw_grid(c, w, h):
    offset_x = (w // 2) % state.CELL_SIZE
    offset_y = (h // 2) % state.CELL_SIZE

    for x in range(offset_x, w, state.CELL_SIZE):
        c.create_line(x, 0, x, h, fill='#E0E0E0')
    for y in range(offset_y, h, state.CELL_SIZE):
        c.create_line(0, y, w, y, fill='#E0E0E0')


def draw_axes(c, w, h):
    cx, cy = w // 2, h // 2
    c.create_line(cx, 0, cx, h, fill='#808080', width=2)
    c.create_line(0, cy, w, cy, fill='#808080', width=2)


def draw_pixel(pixel, color, highlight=False):
    sx, sy = grid_to_screen(pixel.point.x, pixel.point.y)
    size = state.CELL_SIZE - 1

    if pixel.intensity < 1.0:
        r = int(int(color[1:3], 16) * pixel.intensity)
        g = int(int(color[3:5], 16) * pixel.intensity)
        b = int(int(color[5:7], 16) * pixel.intensity)
        color = f'#{r:02x}{g:02x}{b:02x}'

    c = state.canvas
    c.create_rectangle(sx + 2, sy + 2, sx + size, sy + size, fill=color, outline='')

    if highlight:
        c.create_rectangle(sx + 2, sy + 2, sx + size, sy + size, outline='#FF0000', width=2)


def update_status(text):
    state.status_label.config(text=text)