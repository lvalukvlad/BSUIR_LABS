import tkinter as tk
import state
from ui.canvas import create as canvas_create, redraw
from ui.keyboard import bind_keys


def create_menu():
    import os
    
    menubar = tk.Menu(state.root)
    state.root.config(menu=menubar)
    
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Файл", menu=file_menu)
    file_menu.add_command(label="Загрузить объект...", command=load_object)
    file_menu.add_separator()
    
    sample_menu = tk.Menu(file_menu, tearoff=0)
    file_menu.add_cascade(label="Загрузить пример", menu=sample_menu)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lab_dir = os.path.dirname(script_dir)
    
    samples = [
        ("Куб (cube.txt)", "cube.txt"),
        ("Пирамида (pyramid.txt)", "pyramid.txt"),
        ("Тетраэдр (tetrahedron.txt)", "tetrahedron.txt"),
        ("Октаэдр (octahedron.txt)", "octahedron.txt"),
        ("Додекаэдр (dodecahedron.txt)", "dodecahedron.txt"),
        ("Дом (house.txt)", "house.txt"),
        ("Конус (cone.txt)", "cone.txt"),
    ]
    
    for label, filename in samples:
        sample_menu.add_command(label=label, command=lambda f=filename: load_sample(f))
    
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=state.root.quit)
    
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Справка", menu=help_menu)
    help_menu.add_command(label="Управление", command=show_help)


def show_help():
    help_text = """Управление:

Перемещение:
  Стрелки     - перемещение по X/Y
  Page Up/Down - перемещение по Z

Поворот:
  Q/A         - поворот вокруг X
  W/S         - поворот вокруг Y
  E/D         - поворот вокруг Z

Масштабирование:
  +           - увеличить
  -           - уменьшить

Отражение:
  X           - отражение по X
  Y           - отражение по Y
  Z           - отражение по Z

Прочее:
  P           - перспектива ВКЛ/ВЫКЛ
  Esc         - сброс преобразований
"""
    top = tk.Toplevel(state.root)
    top.title("Управление")
    top.geometry("400x400")
    tk.Text(top, wrap=tk.WORD, height=20, width=50).pack(padx=10, pady=10)
    text_widget = top.children.get('!text')
    if text_widget:
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')


def load_object():
    from tkinter import filedialog
    filename = filedialog.askopenfilename(
        title="Выберите файл с 3D объектом",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filename:
        load_from_file(filename)


def load_sample(filename):
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lab_dir = os.path.dirname(script_dir)
    filepath = os.path.join(lab_dir, filename)
    load_from_file(filepath)


def load_from_file(filepath):
    try:
        state.vertices.clear()
        state.edges.clear()
        with open(filepath, 'r') as f:
            reading_vertices = True
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    if line == '#edges':
                        reading_vertices = False
                    continue
                parts = line.split()
                if reading_vertices:
                    if len(parts) >= 3:
                        state.vertices.append([float(parts[0]), float(parts[1]), float(parts[2])])
                else:
                    if len(parts) >= 2:
                        state.edges.append([int(parts[0]), int(parts[1])])
        
        from ui.keyboard import rebuild_transform_matrix
        rebuild_transform_matrix()
        
        redraw()
        from ui.canvas import update_status
        update_status(f"Загружено: {len(state.vertices)} вершин, {len(state.edges)} ребер | {os.path.basename(filepath)}")
    except Exception as e:
        from ui.canvas import update_status
        update_status(f"Ошибка загрузки: {e}")


def create():
    state.root.title("3D Геометрические преобразования")
    state.root.geometry("1000x700")
    
    top_frame = tk.Frame(state.root)
    top_frame.pack(side=tk.TOP, fill=tk.X)
    
    state.status_label = tk.Label(top_frame, text="Кликните на холст, затем используйте клавиши. Стрелки - перемещение, Q/A/W/S/E/D - поворот, +/- масштаб, X/Y/Z - отражение, P - перспектива", 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W)
    state.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    create_menu()
    canvas_create()
    
    state.root.bind('<Key>', handle_keyboard)
    state.root.focus_force()
    
    state.canvas.bind('<Configure>', lambda e: redraw())


def handle_keyboard(event):
    from ui.keyboard import handle_key
    handle_key(event)


def run():
    create()
    state.root.mainloop()
