import os
import uuid
import json
import tkinter as tk
from tkinter import simpledialog, filedialog, scrolledtext, ttk, messagebox, Menu, colorchooser
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.layout import spring_layout, kamada_kawai_layout, shell_layout, circular_layout
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.graph_io import save_graph, load_graph
from PIL import Image, ImageTk  # Для работы с иконками
from shapely.geometry import LineString, Point  # Для определения близости к дугам
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

CONFIG_FILE = 'config.json'


class GraphEditor(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure_style()
        self.graphs = {}
        self.current_graph = None
        self.selected_nodes = set()
        self.selected_edges = set()
        self.clipboard_nodes = []
        self.clipboard_edges = []
        self.node_shapes = ['o', 's', '^', 'D', 'v', 'h', '8', 'p']
        self.current_node_shape = 'o'  # Default shape
        self.figure = plt.Figure(figsize=(20, 15), dpi=100)  # Увеличен размер фигуры
        self.canvas_tkagg = None
        self.node_positions = {}
        self.dragging_node = None
        self.offset_x = 0
        self.offset_y = 0
        self.icons = {}
        self.edge_styles = ['solid', 'dashed', 'dotted', 'dashdot']
        self.current_edge_style = 'solid'
        self.edge_thickness = 1.0
        self.layout_algorithms = {
            "Spring": spring_layout,
            "Kamada-Kawai": kamada_kawai_layout,
            "Shell": shell_layout,
            "Circular": circular_layout
        }
        self.current_layout = "Spring"
        self.settings = {}
        self.move_mode = False  # Режим перемещения узла
        self.node_to_move = None
        self.original_position = None  # Для отмены перемещения
        self.load_icons()
        self.load_settings()
        self.create_widgets()
        self.bind_events()
        self.node_offset = 1.0  # Увеличено смещение для новых узлов

    def configure_style(self):
        style = ttk.Style()
        style.theme_use('clam')  # Выберите подходящую тему

        # Настройка стиля для статусной строки
        style.configure("Status.TLabel",
                        background="#f0f0f0",
                        foreground="black",
                        relief="sunken",
                        anchor="w")

        # Настройка стилей для кнопок
        style.configure("TButton",
                        padding=6,
                        relief="flat",
                        background="#ccc")

        # Настройка стилей для комбобоксов
        style.configure("TCombobox",
                        fieldbackground="white",
                        background="lightgray")

    def load_icons(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
        icon_files = {
            "add": "add.png",
            "delete": "delete.png",
            "rename": "rename.png",
            "color": "color.png",
            "save": "save.png",
            "load": "load.png",
            "info": "info.png",
            "copy": "copy.png",
            "paste": "paste.png",
            "help": "help.png",
            "move": "move.png",
            "highlight": "highlight.png",
            "change_color": "change_color.png",  # Добавлена иконка для изменения цвета
            "incidence_matrix": "matrix.png",   # Иконка для матрицы инцидентности
            "transform_tree": "tree.png"        # Иконка для преобразования в дерево
        }
        for key, filename in icon_files.items():
            try:
                image = Image.open(os.path.join(icon_path, filename))
                if hasattr(Image, 'Resampling'):
                    resample_mode = Image.Resampling.LANCZOS
                else:
                    resample_mode = Image.ANTIALIAS
                image = image.resize((16, 16), resample=resample_mode)
                self.icons[key] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Не удалось загрузить иконку {filename}: {e}")
                self.icons[key] = None

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            self.current_node_shape = self.settings.get('node_shape', 'o')
            self.current_layout = self.settings.get('layout', 'Spring')
            self.current_edge_style = self.settings.get('edge_style', 'solid')
            self.edge_thickness = self.settings.get('edge_thickness', 1.0)
            theme = self.settings.get('theme')
            if theme:
                try:
                    ttk.Style().theme_use(theme)
                except:
                    pass

    def save_settings(self):
        self.settings['node_shape'] = self.current_node_shape
        self.settings['layout'] = self.current_layout
        self.settings['edge_style'] = self.current_edge_style
        self.settings['edge_thickness'] = self.edge_thickness
        self.settings['theme'] = ttk.Style().theme_use()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        # Верхняя панель инструментов
        self.toolbar = ttk.Frame(self)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.toolbar.columnconfigure(8, weight=1)  # Изменено для предотвращения перекрытия

        # Привязка клавиши Escape
        self.master.bind('<Escape>', self.cancel_move)

        # Выбор темы пользователя
        ttk.Label(self.toolbar, text="Тема:").grid(row=0, column=0, sticky="w")
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(
            self.toolbar, textvariable=self.theme_var,
            values=ttk.Style().theme_names(), state="readonly"
        )
        self.theme_combo.grid(row=0, column=1, sticky="w", padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        current_theme = ttk.Style().theme_use()
        self.theme_combo.set(current_theme)

        # Выбор алгоритма раскладки
        ttk.Label(self.toolbar, text="Алгоритм раскладки:").grid(row=0, column=2, sticky="w")
        self.layout_var = tk.StringVar()
        self.layout_combo = ttk.Combobox(
            self.toolbar, textvariable=self.layout_var,
            values=list(self.layout_algorithms.keys()), state="readonly"
        )
        self.layout_combo.grid(row=0, column=3, sticky="w", padx=5)
        self.layout_combo.bind("<<ComboboxSelected>>", self.change_layout)
        self.layout_combo.set(self.current_layout)

        # Кнопка "Переместить узел"
        self.move_button = ttk.Button(
            self.toolbar, text="Переместить узел",
            image=self.icons.get("move"),
            compound="left",
            command=self.activate_move_mode
        )
        self.move_button.grid(row=0, column=4, sticky="w", padx=5)

        # Кнопка справки
        self.help_button = ttk.Button(
            self.toolbar, text="Помощь",
            image=self.icons.get("help"),
            compound="left",
            command=self.show_help
        )
        self.help_button.grid(row=0, column=5, sticky="e", padx=5)

        # Кнопка информации о графе
        self.graph_info_button = ttk.Button(
            self.toolbar, text="Информация о графе",
            image=self.icons.get("incidence_matrix"),
            compound="left",
            command=self.graph_info_extended
        )
        self.graph_info_button.grid(row=0, column=6, sticky="e", padx=5)

        # Кнопка преобразования в дерево
        self.transform_tree_button = ttk.Button(
            self.toolbar, text="Преобразовать в дерево",
            image=self.icons.get("transform_tree"),
            compound="left",
            command=self.transform_to_tree_menu
        )
        self.transform_tree_button.grid(row=0, column=7, sticky="e", padx=5)

        # Создание кнопок "Копировать" и "Вставить"
        self.create_clipboard_buttons()

        # Notebook для вкладок
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)

        # Вкладки
        self.graph_frame = ttk.Frame(self.notebook)
        self.node_frame = ttk.Frame(self.notebook)
        self.edge_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.file_frame = ttk.Frame(self.notebook)
        self.instructions_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.graph_frame, text="Граф")
        self.notebook.add(self.node_frame, text="Узел")
        self.notebook.add(self.edge_frame, text="Ребро")
        self.notebook.add(self.analysis_frame, text="Анализ")
        self.notebook.add(self.file_frame, text="Файл")
        self.notebook.add(self.instructions_frame, text="Инструкция")

        # Вкладка "Граф"
        ttk.Label(self.graph_frame, text="Название графа:").grid(row=0, column=0, sticky="w", pady=2)
        self.graph_name_entry = ttk.Entry(self.graph_frame)
        self.graph_name_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        self.graph_frame.columnconfigure(1, weight=1)
        self.graph_name_entry.bind("<Return>", lambda event: self.add_graph())

        self.directed_var = tk.BooleanVar()
        self.directed_check = ttk.Checkbutton(
            self.graph_frame, text="Ориентированный граф",
            variable=self.directed_var
        )
        self.directed_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        self.add_graph_button = ttk.Button(
            self.graph_frame, text="Добавить граф",
            image=self.icons.get("add"),
            compound="left",
            command=self.add_graph
        )
        self.add_graph_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2)

        self.graph_listbox = tk.Listbox(
            self.graph_frame, selectmode=tk.SINGLE,
            exportselection=False
        )
        self.graph_listbox.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)
        self.graph_frame.rowconfigure(3, weight=1)
        self.graph_listbox.bind('<<ListboxSelect>>', self.on_graph_select)

        # Вкладка "Узел" с добавлением скроллбара
        self.node_canvas = tk.Canvas(self.node_frame)
        self.node_scrollbar = ttk.Scrollbar(self.node_frame, orient="vertical", command=self.node_canvas.yview)
        self.node_scrollable_frame = ttk.Frame(self.node_canvas)

        self.node_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.node_canvas.configure(
                scrollregion=self.node_canvas.bbox("all")
            )
        )

        self.node_canvas.create_window((0, 0), window=self.node_scrollable_frame, anchor="nw")
        self.node_canvas.configure(yscrollcommand=self.node_scrollbar.set)

        self.node_canvas.grid(row=0, column=0, sticky="nsew")
        self.node_scrollbar.grid(row=0, column=1, sticky="ns")

        self.node_frame.rowconfigure(0, weight=1)
        self.node_frame.columnconfigure(0, weight=1)

        # Перенос кнопок в scrollable_frame с корректным отображением команд
        buttons = [
            ("Добавить узел", "add"),
            ("Удалить выбранные узлы", "delete"),
            ("Переименовать узел", "rename"),
            ("Изменить цвет узла", "color"),
            ("Копировать", "copy"),
            ("Вставить", "paste")
        ]

        # Маппинг кнопок на методы
        button_commands = {
            "Добавить узел": self.add_node_selection,
            "Удалить выбранные узлы": self.delete_selection,
            "Переименовать узел": self.rename_node_selection,
            "Изменить цвет узла": self.color_node_selection,
            "Копировать": self.copy_selection,
            "Вставить": self.paste_selection
        }

        for idx, (text, icon) in enumerate(buttons):
            command = button_commands.get(text, lambda: None)
            button = ttk.Button(
                self.node_scrollable_frame, text=text,
                image=self.icons.get(icon),
                compound="left",
                command=command
            )
            button.grid(row=idx, column=0, sticky="ew", pady=2, padx=5)

        # Вкладка "Ребро"
        ttk.Label(self.edge_frame, text="Стиль линии:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
        self.edge_style_var = tk.StringVar(value=self.current_edge_style)
        self.edge_style_combo = ttk.Combobox(
            self.edge_frame, textvariable=self.edge_style_var,
            values=self.edge_styles, state="readonly"
        )
        self.edge_style_combo.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        self.edge_style_combo.bind("<<ComboboxSelected>>", self.change_edge_style)
        self.edge_frame.columnconfigure(1, weight=1)

        ttk.Label(self.edge_frame, text="Толщина линии:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
        self.edge_thickness_var = tk.DoubleVar(value=self.edge_thickness)
        self.edge_thickness_spin = ttk.Spinbox(
            self.edge_frame, from_=0.5, to=5.0, increment=0.5,
            textvariable=self.edge_thickness_var, command=self.change_edge_thickness
        )
        self.edge_thickness_spin.grid(row=1, column=1, sticky="w", pady=2, padx=5)

        self.add_edge_button = ttk.Button(
            self.edge_frame, text="Добавить ребро",
            image=self.icons.get("add"),
            compound="left",
            command=self.add_edge
        )
        self.add_edge_button.grid(row=2, column=0, sticky="ew", pady=2, padx=5)

        self.delete_edge_button = ttk.Button(
            self.edge_frame, text="Удалить ребро",
            image=self.icons.get("delete"),
            compound="left",
            command=self.delete_selection  # Используем общий метод удаления
        )
        self.delete_edge_button.grid(row=3, column=0, sticky="ew", pady=2, padx=5)

        # Кнопка изменения цвета ребра
        self.change_edge_color_button = ttk.Button(
            self.edge_frame, text="Изменить цвет ребра",
            image=self.icons.get("change_color"),
            compound="left",
            command=self.change_edge_color
        )
        self.change_edge_color_button.grid(row=4, column=0, sticky="ew", pady=2, padx=5)

        # Вкладка "Анализ"
        ttk.Label(self.analysis_frame, text="Функции анализа:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
        self.graph_info_button_analysis = ttk.Button(
            self.analysis_frame, text="Информация о графе",
            image=self.icons.get("info"),
            compound="left",
            command=self.graph_info_extended
        )
        self.graph_info_button_analysis.grid(row=1, column=0, sticky="ew", pady=2, padx=5)

        self.is_tree_button = ttk.Button(
            self.analysis_frame, text="Проверить дерево",
            command=self.is_tree
        )
        self.is_tree_button.grid(row=2, column=0, sticky="ew", pady=2, padx=5)

        self.eulerian_cycle_button = ttk.Button(
            self.analysis_frame, text="Эйлеров цикл",
            command=self.eulerian_cycle
        )
        self.eulerian_cycle_button.grid(row=3, column=0, sticky="ew", pady=2, padx=5)

        self.all_eulerian_cycles_button = ttk.Button(
            self.analysis_frame, text="Все Эйлеровы циклы",
            command=self.all_eulerian_cycles
        )
        self.all_eulerian_cycles_button.grid(row=4, column=0, sticky="ew", pady=2, padx=5)

        self.shortest_path_button = ttk.Button(
            self.analysis_frame, text="Кратчайший путь",
            command=self.shortest_path
        )
        self.shortest_path_button.grid(row=5, column=0, sticky="ew", pady=2, padx=5)

        self.all_paths_button = ttk.Button(
            self.analysis_frame, text="Все пути",
            command=self.find_all_paths
        )
        self.all_paths_button.grid(row=6, column=0, sticky="ew", pady=2, padx=5)

        self.calculate_distance_button = ttk.Button(
            self.analysis_frame, text="Вычислить расстояние",
            command=self.calculate_distance
        )
        self.calculate_distance_button.grid(row=7, column=0, sticky="ew", pady=2, padx=5)

        # Вкладка "Файл"
        self.save_graph_button = ttk.Button(
            self.file_frame, text="Сохранить граф",
            image=self.icons.get("save"),
            compound="left",
            command=self.save_graph
        )
        self.save_graph_button.grid(row=0, column=0, sticky="ew", pady=2, padx=5)

        self.load_graph_button = ttk.Button(
            self.file_frame, text="Загрузить граф",
            image=self.icons.get("load"),
            compound="left",
            command=self.load_graph
        )
        self.load_graph_button.grid(row=1, column=0, sticky="ew", pady=2, padx=5)

        # Вкладка "Инструкция"
        instruction_text = (
            "Добро пожаловать в Полнофункциональный Графовый Редактор!\n\n"
            "Основные функции:\n"
            "1. **Граф**: Создавайте и управляйте несколькими графами.\n"
            "2. **Узел**: Добавляйте, удаляйте, переименовывайте и окрашивайте узлы. Копируйте и вставляйте узлы.\n"
            "3. **Ребро**: Добавляйте и удаляйте ребра между узлами. Настраивайте стиль, толщину и цвет линий.\n"
            "4. **Анализ**: Получайте информацию о графе, проверяйте, является ли граф деревом, находите Эйлеров цикл и кратчайшие пути.\n"
            "5. **Файл**: Сохраняйте и загружайте графы.\n\n"
            "Используйте меню выбора темы и алгоритма раскладки для изменения внешнего вида и расположения графа. Для получения дополнительной информации нажмите кнопку 'Помощь'.\n\n"
            "Чтобы переместить узел, нажмите кнопку 'Переместить узел', затем кликните на узел и выберите новое место для его размещения.\n\n"
            "Чтобы удалить узел или ребро, выделите его и нажмите кнопку 'Удалить выбранные узлы' или 'Удалить ребро'.\n\n"
            "Чтобы изменить цвет ребра, выделите его и нажмите кнопку 'Изменить цвет ребра'.\n\n"
            "Дополнительные функции находятся во вкладке 'Анализ'."
        )
        self.instructions_label = scrolledtext.ScrolledText(
            self.instructions_frame, wrap=tk.WORD,
            bg="#f0f0f0", font=("Arial", 10)
        )
        self.instructions_label.insert(tk.END, instruction_text)
        self.instructions_label.config(state=tk.DISABLED)
        self.instructions_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.instructions_frame.rowconfigure(0, weight=1)
        self.instructions_frame.columnconfigure(0, weight=1)

        # Основная область для графа
        self.figure_frame = ttk.Frame(self)
        self.figure_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Статусная строка
        self.status_bar = ttk.Label(
            self, text="Готово", style="Status.TLabel",
            anchor="w"
        )
        self.status_bar.grid(row=3, column=0, sticky="ew")

    def create_clipboard_buttons(self):
        # Создание кнопок "Копировать" и "Вставить"
        clipboard_frame = ttk.Frame(self.toolbar)
        clipboard_frame.grid(row=0, column=8, sticky="e", padx=5)

        self.copy_button = ttk.Button(
            clipboard_frame, text="Копировать",
            image=self.icons.get("copy"),
            compound="left",
            command=self.copy_selection
        )
        self.copy_button.grid(row=0, column=0, padx=2)

        self.paste_button = ttk.Button(
            clipboard_frame, text="Вставить",
            image=self.icons.get("paste"),
            compound="left",
            command=self.paste_selection
        )
        self.paste_button.grid(row=0, column=1, padx=2)

    def bind_events(self):
        self.canvas.mpl_connect("button_press_event", self.on_mouse_event)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_event)  # Изменено
        self.canvas.mpl_connect("button_release_event", self.on_mouse_event)  # Изменено
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.master.bind('<Escape>', self.cancel_move)
        # Добавление привязки выделения при двойном клике
        # Возможно, уже реализовано в on_mouse_event

    def cancel_move(self, event=None):
        if self.move_mode and self.node_to_move:
            # Восстановить исходную позицию
            self.node_positions[id(self.current_graph)][self.node_to_move] = self.original_position
            self.current_graph.nodes[self.node_to_move]['pos'] = self.original_position
            self.draw_graph()
            self.log_message(f"Перемещение узла '{self.node_to_move}' отменено.")
            self.status_bar.config(text=f"Перемещение узла '{self.node_to_move}' отменено.")
            self.move_mode = False
            self.node_to_move = None
            self.original_position = None

    def activate_move_mode(self):
        self.move_mode = True
        self.log_message("Режим перемещения узла активирован. Выберите узел для перемещения.")
        self.status_bar.config(text="Режим перемещения узла активирован. Выберите узел для перемещения.")

    def on_right_click(self, event):
        if self.current_graph is None:
            return
        if event.inaxes is None:
            return
        try:
            click_x, click_y = event.xdata, event.ydata
            pos = self.node_positions.get(id(self.current_graph), {})
            clicked_node = None
            for node, (x, y) in pos.items():
                dx = click_x - x
                dy = click_y - y
                distance = (dx**2 + dy**2)**0.5
                threshold = 0.1
                if distance < threshold:
                    clicked_node = node
                    break
            if clicked_node:
                menu = Menu(self, tearoff=0)
                menu.add_command(label="Переименовать", command=lambda: self.rename_node(clicked_node))
                menu.add_command(label="Изменить цвет", command=lambda: self.change_node_color())
                menu.add_command(label="Изменить форму", command=lambda: self.change_node_shape_specific(clicked_node))
                menu.add_command(label="Удалить узел", command=lambda: self.delete_single_node(clicked_node))
                menu.add_command(label="Переместить узел", command=lambda: self.start_move_node(clicked_node))
                menu.add_separator()
                menu.add_command(label="Выделить", command=lambda: self.highlight_element(clicked_node))
                try:
                    menu.tk_popup(int(event.guiEvent.x_root), int(event.guiEvent.y_root))
                finally:
                    menu.grab_release()

            else:
                # Проверка на ребро
                clicked_edge = None
                pos = self.node_positions.get(id(self.current_graph), {})
                for (u, v) in self.current_graph.edges():
                    if self.is_near_edge(event.xdata, event.ydata, pos[u], pos[v]):
                        clicked_edge = (u, v)
                        break
                if clicked_edge:
                    menu = Menu(self, tearoff=0)
                    menu.add_command(label="Удалить ребро", command=lambda: self.delete_edge_single(clicked_edge))
                    menu.add_command(label="Изменить цвет ребра", command=lambda: self.change_edge_color_single(clicked_edge))
                    menu.add_separator()
                    menu.add_command(label="Выделить", command=lambda: self.highlight_element(clicked_edge))
                    try:
                        menu.tk_popup(int(event.guiEvent.x_root), int(event.guiEvent.y_root))
                    finally:
                        menu.grab_release()

        except Exception as e:
            self.log_message(f"Ошибка при открытии контекстного меню: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось открыть контекстное меню: {e}")

    def delete_edge_single(self, edge):
        if self.current_graph is None or edge is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Не выбрано ребро", "Пожалуйста, выберите ребро для удаления.")
            self.log_message("Не выбрано ребро для удаления.")
            return
        if self.master.winfo_exists():
            confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить ребро '{edge[0]}' -> '{edge[1]}'?")
            if not confirm:
                self.log_message(f"Удаление ребра '{edge[0]}' -> '{edge[1]}' отменено пользователем.")
                return
        self.current_graph.remove_edge(*edge)
        self.log_message(f"Ребро '{edge[0]}' -> '{edge[1]}' удалено.")
        self.selected_edges.discard(edge)
        self.draw_graph()
        self.save_settings()

    def change_edge_color_single(self, edge):
        if self.current_graph is None or edge is None:
            self.log_message("Не выбрано ребро для изменения цвета.")
            if self.master.winfo_exists():
                messagebox.showwarning("Не выбрано ребро", "Пожалуйста, выберите ребро для изменения цвета.")
            return
        color = colorchooser.askcolor(title="Выберите цвет для ребра")[1]
        if color:
            self.current_graph.edges[edge]['color'] = color
            self.log_message(f"Цвет ребра '{edge[0]}' -> '{edge[1]}' изменен на '{color}'.")
            self.draw_graph()
            self.save_settings()

    def highlight_element(self, element):
        if isinstance(element, tuple):
            # Это ребро
            if element in self.selected_edges:
                self.selected_edges.remove(element)
                self.log_message(f"Дуга '{element[0]}' -> '{element[1]}' снята с выделения.")
            else:
                self.selected_edges.add(element)
                self.log_message(f"Дуга '{element[0]}' -> '{element[1]}' выделена.")
        else:
            # Это узел
            if element in self.selected_nodes:
                self.selected_nodes.remove(element)
                self.log_message(f"Узел '{element}' снят с выделения.")
            else:
                self.selected_nodes.add(element)
                self.log_message(f"Узел '{element}' выделен.")
        self.draw_graph()
        self.save_settings()

    def on_mouse_event(self, event):
        if event.button == 3:
            self.on_right_click(event)
            return

        if event.name == "button_press_event" and event.button == 1:
            self.on_mouse_down(event)
            return

        if event.name == "button_release_event" and event.button == 1:
            self.on_mouse_up(event)
            return

    def on_hover(self, event):
        # Здесь можно реализовать отображение подсказок или другой функционал при наведении
        pass

    def on_mouse_down(self, event):
        if self.current_graph is None:
            return
        if event.inaxes is None:
            return
        try:
            click_x, click_y = event.xdata, event.ydata
            pos = self.node_positions.get(id(self.current_graph), {})
            # Проверка на выбор узла
            for node, (x, y) in pos.items():
                dx = click_x - x
                dy = click_y - y
                distance = (dx**2 + dy**2)**0.5
                threshold = 0.1
                if distance < threshold:
                    if event.guiEvent.state & 0x0001:  # Shift key pressed
                        if node in self.selected_nodes:
                            self.selected_nodes.remove(node)
                            self.log_message(f"Узел '{node}' снят с выделения.")
                        else:
                            self.selected_nodes.add(node)
                            self.log_message(f"Узел '{node}' выделен.")
                    else:
                        if node in self.selected_nodes and len(self.selected_nodes) == 1:
                            self.selected_nodes.clear()
                            self.log_message(f"Узел '{node}' снят с выделения.")
                        else:
                            self.selected_nodes = {node}
                            self.selected_edges.clear()
                            self.log_message(f"Узел '{node}' выделен.")
                    self.draw_graph()
                    self.save_settings()
                    return
            # Проверка на выбор дуги
            for (u, v) in self.current_graph.edges():
                if self.is_near_edge(event.xdata, event.ydata, pos[u], pos[v]):
                    if event.guiEvent.state & 0x0001:  # Shift key pressed
                        if (u, v) in self.selected_edges:
                            self.selected_edges.remove((u, v))
                            self.log_message(f"Дуга '{u}' -> '{v}' снята с выделения.")
                        else:
                            self.selected_edges.add((u, v))
                            self.log_message(f"Дуга '{u}' -> '{v}' выделена.")
                    else:
                        self.selected_edges = {(u, v)}
                        self.selected_nodes.clear()
                        self.log_message(f"Дуга '{u}' -> '{v}' выделена.")
                    self.draw_graph()
                    self.save_settings()
                    return
            # Если ничего не выбрано
            if not (event.guiEvent.state & 0x0001):
                self.clear_selection()
        except Exception as e:
            self.log_message(f"Ошибка при обработке клика мыши: {e}")

    def on_mouse_up(self, event):
        if self.move_mode and self.node_to_move:
            if event.inaxes is None:
                return
            try:
                new_x, new_y = event.xdata, event.ydata
                self.node_positions[id(self.current_graph)][self.node_to_move] = (new_x, new_y)
                self.current_graph.nodes[self.node_to_move]['pos'] = (new_x, new_y)
                self.draw_graph()
                self.log_message(f"Узел '{self.node_to_move}' перемещен на новое место.")
                self.status_bar.config(text=f"Узел '{self.node_to_move}' перемещен на новое место.")
                self.move_mode = False
                self.node_to_move = None
                self.original_position = None
            except Exception as e:
                self.log_message(f"Ошибка при перемещении узла: {e}")
                if self.master.winfo_exists():
                    messagebox.showerror("Ошибка", f"Не удалось переместить узел: {e}")

    def is_near_edge(self, x, y, pos1, pos2, tolerance=0.05):
            """Проверяет, находится ли точка (x, y) рядом с дугой между pos1 и pos2."""
            line = LineString([pos1, pos2])
            point = Point(x, y)
            return line.distance(point) < tolerance

    def clear_selection(self, event=None):
        if self.selected_nodes or self.selected_edges:
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Выбор отменен.")

    def change_edge_style(self, event):
        self.current_edge_style = self.edge_style_var.get()
        self.log_message(f"Стиль ребер изменен на '{self.current_edge_style}'.")
        self.draw_graph()
        self.save_settings()

    def change_edge_thickness(self):
        self.edge_thickness = self.edge_thickness_var.get()
        self.log_message(f"Толщина ребер изменена на '{self.edge_thickness}'.")
        self.draw_graph()
        self.save_settings()

    def change_layout(self, event):
        self.current_layout = self.layout_var.get()
        self.log_message(f"Алгоритм раскладки изменен на '{self.current_layout}'.")
        self.draw_graph()
        self.save_settings()

    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        try:
            ttk.Style().theme_use(selected_theme)
            self.log_message(f"Тема изменена на '{selected_theme}'.")
            self.draw_graph()
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при смене темы: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось сменить тему: {e}")

    def change_node_shape(self, event):
        selected_shape = self.node_shape_var.get()
        self.current_node_shape = selected_shape
        self.draw_graph()
        self.log_message(f"Форма узлов изменена на '{selected_shape}'.")
        self.save_settings()

    def add_graph(self):
        name = self.graph_name_entry.get().strip()
        if not name:
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка ввода", "Название графа не может быть пустым.")
            self.log_message("Название графа не может быть пустым.")
            return
        if name in self.graphs:
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка ввода", f"Граф '{name}' уже существует.")
            self.log_message(f"Граф '{name}' уже существует.")
            return
        directed = self.directed_var.get()
        graph = nx.DiGraph() if directed else nx.Graph()
        self.graphs[name] = graph
        self.graph_listbox.insert(tk.END, name)
        self.graph_name_entry.delete(0, tk.END)
        self.log_message(f"Граф '{name}' добавлен. Ориентированный: {directed}")
        self.save_settings()

    def on_graph_select(self, event):
        selection = event.widget.curselection()
        if selection:
            g_name = event.widget.get(selection[0])
            self.current_graph = self.graphs[g_name]
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message(f"Граф '{g_name}' выбран.")
            self.save_settings()

    # Методы, связанные с кнопками во вкладке "Узел"
    def add_node_selection(self):
        self.add_node()

    def delete_selection(self):
        # Удаление выбранных узлов и дуг
        # Удаление выбранных узлов
        for node in list(self.selected_nodes):
            if node in self.current_graph:
                self.current_graph.remove_node(node)
                self.log_message(f"Узел '{node}' удален.")
        self.selected_nodes.clear()
        # Удаление выбранных дуг
        for edge in list(self.selected_edges):
            if self.current_graph.has_edge(*edge):
                self.current_graph.remove_edge(*edge)
                self.log_message(f"Ребро '{edge[0]}' -> '{edge[1]}' удалено.")
        self.selected_edges.clear()
        self.draw_graph()
        self.save_settings()

    def rename_node_selection(self):
        if self.selected_nodes:
            self.rename_node(next(iter(self.selected_nodes), None))
        else:
            self.log_message("Нет выбранных узлов для переименования.")
            if self.master.winfo_exists():
                messagebox.showwarning("Не выбраны узлы", "Пожалуйста, выберите узел для переименования.")

    def color_node_selection(self):
        self.change_node_color()

    def copy_selection(self):
        if not self.selected_nodes and not self.selected_edges:
            self.log_message("Нет выбранных элементов для копирования.")
            return

        self.clipboard_nodes = list(self.selected_nodes)
        self.clipboard_edges = list(self.selected_edges)
        self.log_message(f"Скопировано узлов: {self.clipboard_nodes} и дуг: {self.clipboard_edges}")

    def paste_selection(self):
        if not self.clipboard_nodes and not self.clipboard_edges:
            self.log_message("Буфер обмена пуст.")
            return

        node_mapping = {}
        # Копирование узлов
        for node in self.clipboard_nodes:
            new_node = f"{node}_{uuid.uuid4().hex[:6]}"
            attrs = self.current_graph.nodes[node].copy()
            # Смещение позиции для визуальной разницы
            old_pos = self.node_positions[id(self.current_graph)].get(node, (0, 0))
            attrs['pos'] = (old_pos[0] + self.node_offset, old_pos[1] + self.node_offset)
            attrs['content'] = '' if not attrs.get('content') else attrs['content']
            self.current_graph.add_node(new_node, **attrs)
            self.node_positions[id(self.current_graph)][new_node] = attrs['pos']
            node_mapping[node] = new_node
            self.log_message(f"Вставлен узел '{new_node}', копия '{node}'.")

        # Копирование дуг
        for edge in self.clipboard_edges:
            u, v = edge
            new_u = node_mapping.get(u, u)
            new_v = node_mapping.get(v, v)
            if not self.current_graph.has_edge(new_u, new_v):
                attrs = self.current_graph.edges[edge].copy()
                self.current_graph.add_edge(new_u, new_v, **attrs)
                self.log_message(f"Вставлена дуга '{new_u}' -> '{new_v}'.")

        self.draw_graph()
        self.log_message("Вставка завершена.")
        self.save_settings()

    def add_node(self, position=None):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        node_id = simpledialog.askstring("Добавить узел", "Введите название узла (оставьте пустым для автоматической генерации):")
        if node_id is None:
            self.log_message("Добавление узла отменено пользователем.")
            return
        node_id = node_id.strip()
        if not node_id:
            node_id = f"node_{uuid.uuid4().hex[:6]}"
        if node_id in self.current_graph:
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", f"Узел '{node_id}' уже существует.")
            self.log_message(f"Узел '{node_id}' уже существует.")
            return
        if position is None:
            # Автоматическое смещение новой позиции
            pos = self.node_positions.get(id(self.current_graph), {})
            if pos:
                last_pos = list(pos.values())[-1]
                position = (last_pos[0] + self.node_offset, last_pos[1] + self.node_offset)
            else:
                position = (0, 0)
        default_color = 'skyblue'
        self.current_graph.add_node(node_id, content=node_id if not node_id.startswith("node_") else '', color=default_color, pos=position, shape=self.current_node_shape)
        self.node_positions[id(self.current_graph)] = self.node_positions.get(id(self.current_graph), {})
        self.node_positions[id(self.current_graph)][node_id] = position
        self.draw_graph()
        self.log_message(f"Узел '{node_id}' добавлен.")
        self.save_settings()

    def rename_node(self, node):
        if self.current_graph is None or node is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Не выбран узел", "Пожалуйста, выберите узел для переименования.")
            self.log_message("Не выбран узел для переименования.")
            return
        new_name = simpledialog.askstring("Переименовать узел", f"Введите новое название для узла '{node}':")
        if new_name is not None and new_name.strip() != "":
            new_name = new_name.strip()
            if new_name in self.current_graph:
                if self.master.winfo_exists():
                    messagebox.showwarning("Ошибка", f"Узел '{new_name}' уже существует.")
                self.log_message(f"Узел '{new_name}' уже существует.")
                return
            if node in self.node_positions.get(id(self.current_graph), {}):
                self.node_positions[id(self.current_graph)][new_name] = self.node_positions[id(self.current_graph)].pop(node)
            self.current_graph = nx.relabel_nodes(self.current_graph, {node: new_name})
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.remove(node)
            self.selected_nodes.add(new_name)
            self.selected_edges = {(new_name if u == node else u, new_name if v == node else v) for (u, v) in self.selected_edges}
            self.draw_graph()
            self.log_message(f"Узел '{node}' переименован в '{new_name}'.")
            self.save_settings()

    def is_valid_color_method(self, color):
        return self.is_valid_color(color)

    def change_node_color(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        if not self.selected_nodes:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранных узлов", "Пожалуйста, выберите узлы для изменения цвета.")
            self.log_message("Нет выбранных узлов для изменения цвета.")
            return
        color = colorchooser.askcolor(title="Выберите цвет для узлов")[1]
        if color:
            if self.is_valid_color(color):
                for node in self.selected_nodes:
                    if node in self.current_graph.nodes:
                        self.current_graph.nodes[node]['color'] = color
                        self.log_message(f"Узел '{node}' окрашен в '{color}'.")
                self.draw_graph()
                self.save_settings()
            else:
                if self.master.winfo_exists():
                    messagebox.showwarning("Некорректный цвет", "Введен некорректный цвет.")
                self.log_message("Введен некорректный цвет.")

    def delete_single_node(self, node):
        if self.current_graph is None or node is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Не выбран узел", "Пожалуйста, выберите узел для удаления.")
            self.log_message("Не выбран узел для удаления.")
            return
        if self.master.winfo_exists():
            confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить узел '{node}'?")
            if not confirm:
                self.log_message(f"Удаление узла '{node}' отменено пользователем.")
                return
        self.current_graph.remove_node(node)
        self.log_message(f"Узел '{node}' удален.")
        self.selected_nodes.discard(node)
        self.draw_graph()
        self.save_settings()

    def graph_info_extended(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        num_nodes = self.current_graph.number_of_nodes()
        num_edges = self.current_graph.number_of_edges()
        degrees = dict(self.current_graph.degree())
        is_tree = nx.is_tree(self.current_graph) if not isinstance(self.current_graph, nx.DiGraph) else False
        incidence_matrix = nx.incidence_matrix(self.current_graph).todense() if not isinstance(self.current_graph, nx.DiGraph) else "Матрица инцидентности для ориентированного графа не поддерживается."

        info = (
            f"Узлы: {num_nodes}\n"
            f"Ребра: {num_edges}\n"
            f"Степени узлов: {degrees}\n"
            f"Является деревом: {'Да' if is_tree else 'Нет'}\n"
            f"Матрица инцидентности:\n{incidence_matrix}"
        )
        self.log_message(info)
        if self.master.winfo_exists():
            messagebox.showinfo("Информация о графе", info)

    def is_tree(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        if isinstance(self.current_graph, nx.DiGraph):
            if self.master.winfo_exists():
                messagebox.showinfo("Проверка", "Данная функция поддерживает только неориентированные графы.")
            self.log_message("Проверка дерева поддерживает только неориентированные графы.")
            return
        if nx.is_tree(self.current_graph):
            self.log_message("Граф является деревом.")
            if self.master.winfo_exists():
                messagebox.showinfo("Проверка", "Граф является деревом.")
        else:
            self.log_message("Граф не является деревом.")
            if self.master.winfo_exists():
                messagebox.showinfo("Проверка", "Граф не является деревом.")

    def eulerian_cycle(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        if isinstance(self.current_graph, nx.DiGraph):
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеров цикл", "Эйлеров цикл не поддерживается для ориентированных графов.")
            self.log_message("Эйлеров цикл не поддерживается для ориентированных графов.")
            return
        if nx.is_eulerian(self.current_graph):
            cycle = list(nx.eulerian_circuit(self.current_graph))
            self.log_message(f"Эйлеров цикл: {cycle}")
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеров цикл", f"Эйлеров цикл: {cycle}")
        else:
            self.log_message("В графе нет Эйлерова цикла.")
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеров цикл", "В графе нет Эйлерова цикла.")

    def all_eulerian_cycles(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        if isinstance(self.current_graph, nx.DiGraph):
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеровы циклы", "Эйлеровы циклы не поддерживаются для ориентированных графов.")
            self.log_message("Эйлеровы циклы не поддерживаются для ориентированных графов.")
            return
        if nx.is_eulerian(self.current_graph):
            cycles = list(nx.eulerian_circuit(self.current_graph))
            self.log_message(f"Эйлеровы циклы: {cycles}")
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеровы циклы", f"Эйлеровы циклы: {cycles}")
        else:
            self.log_message("В графе нет Эйлеровых циклов.")
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеровы циклы", "В графе нет Эйлеровых циклов.")

    def shortest_path(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        nodes = list(self.current_graph.nodes)
        if len(nodes) < 2:
            self.log_message("Недостаточно узлов для поиска кратчайшего пути.")
            if self.master.winfo_exists():
                messagebox.showwarning("Недостаточно узлов", "Недостаточно узлов для поиска кратчайшего пути.")
            return
        start = simpledialog.askstring("Кратчайший путь", "Введите начальный узел:")
        end = simpledialog.askstring("Кратчайший путь", "Введите конечный узел:")
        if start is None or end is None:
            return
        start = start.strip()
        end = end.strip()
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            path = nx.shortest_path(self.current_graph, start, end)
            self.log_message(f"Кратчайший путь от '{start}' до '{end}': {path}")
            if self.master.winfo_exists():
                messagebox.showinfo("Кратчайший путь", f"Кратчайший путь от '{start}' до '{end}': {path}")
        except nx.NetworkXNoPath:
            self.log_message(f"Пути между '{start}' и '{end}' нет.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Пути между '{start}' и '{end}' нет.")
        except nx.NodeNotFound as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Узел не найден: {e}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось найти путь: {e}")

    def find_all_paths(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        nodes = list(self.current_graph.nodes)
        if len(nodes) < 2:
            self.log_message("Недостаточно узлов для поиска путей.")
            if self.master.winfo_exists():
                messagebox.showwarning("Недостаточно узлов", "Недостаточно узлов для поиска путей.")
            return
        start = simpledialog.askstring("Все пути", "Введите начальный узел:")
        end = simpledialog.askstring("Все пути", "Введите конечный узел:")
        if start is None or end is None:
            return
        start = start.strip()
        end = end.strip()
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            paths = list(nx.all_simple_paths(self.current_graph, source=start, target=end))
            if paths:
                self.log_message(f"Все пути от '{start}' до '{end}': {paths}")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Все пути от '{start}' до '{end}':\n{paths}")
            else:
                self.log_message(f"Пути между '{start}' и '{end}' не найдены.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Пути между '{start}' и '{end}' не найдены.")
        except Exception as e:
            self.log_message(f"Ошибка при поиске путей: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось найти пути: {e}")

    def calculate_distance(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        nodes = list(self.current_graph.nodes)
        if len(nodes) < 2:
            self.log_message("Недостаточно узлов для вычисления расстояния.")
            if self.master.winfo_exists():
                messagebox.showwarning("Недостаточно узлов", "Недостаточно узлов для вычисления расстояния.")
            return
        start = simpledialog.askstring("Вычислить расстояние", "Введите начальный узел:")
        end = simpledialog.askstring("Вычислить расстояние", "Введите конечный узел:")
        if start is None or end is None:
            return
        start = start.strip()
        end = end.strip()
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            distance = nx.shortest_path_length(self.current_graph, source=start, target=end)
            self.log_message(f"Расстояние между '{start}' и '{end}': {distance}")
            if self.master.winfo_exists():
                messagebox.showinfo("Расстояние", f"Расстояние между '{start}' и '{end}': {distance}")
        except nx.NetworkXNoPath:
            self.log_message(f"Пути между '{start}' и '{end}' нет.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Пути между '{start}' и '{end}' нет.")
        except nx.NodeNotFound as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Узел не найден: {e}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось вычислить расстояние: {e}")

    def add_edge(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return

        if len(self.selected_nodes) != 2:
            if self.master.winfo_exists():
                messagebox.showwarning("Недостаточно узлов", "Пожалуйста, выберите ровно два узла для добавления ребра.")
            self.log_message("Для добавления ребра необходимо выбрать ровно два узла.")
            return

        node1, node2 = list(self.selected_nodes)
        if self.current_graph.has_edge(node1, node2):
            if self.master.winfo_exists():
                messagebox.showwarning("Ребро существует", f"Ребро между '{node1}' и '{node2}' уже существует.")
            self.log_message(f"Ребро между '{node1}' и '{node2}' уже существует.")
            return

        try:
            self.current_graph.add_edge(node1, node2, style=self.current_edge_style, thickness=self.edge_thickness, color='black')  # Добавлено начальное значение цвета
            self.log_message(f"Ребро добавлено между '{node1}' и '{node2}'.")
            self.draw_graph()
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при добавлении ребра: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось добавить ребро: {e}")

    def save_graph(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф для сохранения.")
            self.log_message("Нет выбранного графа для сохранения.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json")],
            initialdir=os.path.expanduser("~/Desktop")
        )
        if filename:
            try:
                save_graph(self.current_graph, filename)
                self.log_message(f"Граф сохранен как '{filename}'.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Сохранено", f"Граф сохранен как '{filename}'.")
            except Exception as e:
                self.log_message(f"Ошибка при сохранении графа: {e}")
                if self.master.winfo_exists():
                    messagebox.showerror("Ошибка", f"Не удалось сохранить граф: {e}")

    def load_graph(self):
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json")],
            initialdir=os.path.expanduser("~/Desktop")
        )
        if filename:
            try:
                graph = load_graph(filename)
                # Проверка валидности цветов узлов
                default_color = 'skyblue'
                for node, attrs in graph.nodes(data=True):
                    color = attrs.get('color', default_color)
                    if not self.is_valid_color(color):
                        graph.nodes[node]['color'] = default_color
                        self.log_message(f"Некорректный цвет узла '{node}' исправлен на '{default_color}'.")
                name = simpledialog.askstring("Название графа", "Введите название для загруженного графа:")
                if not name:
                    if self.master.winfo_exists():
                        messagebox.showwarning("Ошибка ввода", "Граф должен иметь название.")
                    self.log_message("Граф должен иметь название.")
                    return
                if name in self.graphs:
                    if self.master.winfo_exists():
                        messagebox.showwarning("Ошибка ввода", f"Граф '{name}' уже существует.")
                    self.log_message(f"Граф '{name}' уже существует.")
                    return
                self.graphs[name] = graph
                self.graph_listbox.insert(tk.END, name)
                pos = nx.get_node_attributes(graph, 'pos')
                self.node_positions[id(graph)] = pos
                self.log_message(f"Граф '{name}' загружен из '{filename}'.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Загружено", f"Граф '{name}' загружен из '{filename}'.")
                self.save_settings()
            except Exception as e:
                self.log_message(f"Ошибка при загрузке графа: {e}")
                if self.master.winfo_exists():
                    messagebox.showerror("Ошибка", f"Не удалось загрузить граф: {e}")

    def draw_graph(self):
        if self.current_graph is None:
            return
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#f0f0f0')  # Установка цвета фона графа
        ax.axis('off')  # Скрыть оси

        # Получение или вычисление позиций узлов
        layout_func = self.layout_algorithms.get(self.current_layout, spring_layout)
        try:
            pos = layout_func(self.current_graph)
        except Exception as e:
            self.log_message(f"Ошибка при расчете позиций узлов: {e}")
            pos = nx.spring_layout(self.current_graph)
        self.node_positions[id(self.current_graph)] = pos

        # Обновление позиций из атрибутов узлов
        for node in self.current_graph.nodes:
            if 'pos' in self.current_graph.nodes[node]:
                pos[node] = self.current_graph.nodes[node]['pos']
            else:
                pos[node] = pos.get(node, (0, 0))

        node_colors = [self.current_graph.nodes[n].get('color', 'skyblue') for n in self.current_graph.nodes]
        labels = {n: self.current_graph.nodes[n].get('content', '') for n in self.current_graph.nodes}
        node_shapes = {}
        for n in self.current_graph.nodes:
            shape = self.current_graph.nodes[n].get('shape', self.current_node_shape)
            if shape not in node_shapes:
                node_shapes[shape] = []
            node_shapes[shape].append(n)

        # Проверка валидности цветов
        valid_colors = []
        for color in node_colors:
            if not self.is_valid_color(color):
                valid_colors.append('skyblue')
                self.log_message(f"Некорректный цвет '{color}' заменен на 'skyblue'.")
            else:
                valid_colors.append(color)

        try:
            for shape, nodes in node_shapes.items():
                nx.draw(
                    self.current_graph.subgraph(nodes), pos,
                    with_labels=True, labels=labels,
                    node_size=700, node_color=[self.current_graph.nodes[n].get('color', 'skyblue') for n in nodes],
                    node_shape=shape,
                    font_size=10, font_weight="bold", ax=ax,
                    arrows=True if self.current_graph.is_directed() else False
                )
        except Exception as e:
            self.log_message(f"Ошибка при рисовании узлов: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось нарисовать узлы: {e}")
            return

        # Рисование дуг с учетом стиля, толщины и цвета
        for (u, v, attrs) in self.current_graph.edges(data=True):
            style = attrs.get('style', self.current_edge_style)
            thickness = attrs.get('thickness', self.edge_thickness)
            color = attrs.get('color', 'black')
            if style == 'solid':
                linestyle = 'solid'
            elif style == 'dashed':
                linestyle = 'dashed'
            elif style == 'dotted':
                linestyle = 'dotted'
            elif style == 'dashdot':
                linestyle = 'dashdot'
            else:
                linestyle = 'solid'
            nx.draw_networkx_edges(
                self.current_graph, pos,
                edgelist=[(u, v)],
                ax=ax,
                style=linestyle,
                width=thickness,
                edge_color=color,
                arrows=True if self.current_graph.is_directed() else False
            )

        # Выделение выбранных узлов
        if self.selected_nodes:
            try:
                nx.draw_networkx_nodes(
                    self.current_graph, pos,
                    nodelist=list(self.selected_nodes),
                    node_color='yellow',
                    node_size=700,
                    node_shape=self.current_node_shape,
                    ax=ax
                )
            except Exception as e:
                self.log_message(f"Ошибка при выделении узлов: {e}")
                if self.master.winfo_exists():
                    messagebox.showerror("Ошибка", f"Не удалось выделить узлы: {e}")

        # Выделение выбранных дуг
        if self.selected_edges:
            for edge in self.selected_edges:
                try:
                    nx.draw_networkx_edges(
                        self.current_graph, pos,
                        edgelist=[edge],
                        ax=ax,
                        edge_color='red',
                        width=self.current_graph.edges[edge].get('thickness', self.edge_thickness) + 1,
                        arrows=True if self.current_graph.is_directed() else False
                    )
                except Exception as e:
                    self.log_message(f"Ошибка при выделении дуг: {e}")
                    if self.master.winfo_exists():
                        messagebox.showerror("Ошибка", f"Не удалось выделить дуги: {e}")
        self.canvas.draw()

    def show_help(self):
        # Переключение на вкладку "Инструкция"
        self.notebook.select(self.instructions_frame)
        self.log_message("Открыта вкладка 'Инструкция'.")
        self.status_bar.config(text="Открыта вкладка 'Инструкция'.")

    def is_valid_color(self, color):
        try:
            mcolors.to_rgb(color)
            return True
        except ValueError:
            return False

    def get_current_graph_name(self):
        for name, graph in self.graphs.items():
            if graph == self.current_graph:
                return name
        return None

    def log_message(self, message):
        # Метод для логирования сообщений, можно реализовать дополнительное логирование в UI
        print(message)

    def start_move_node(self, node):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            return
        if node not in self.current_graph:
            self.log_message(f"Узел '{node}' не существует.")
            return
        self.move_mode = True
        self.node_to_move = node
        self.original_position = self.node_positions[id(self.current_graph)].get(node, (0, 0))
        self.log_message(f"Начато перемещение узла '{node}'. Переместите его на новое место.")
        self.status_bar.config(text=f"Начато перемещение узла '{node}'. Переместите его на новое место.")

    def change_node_shape_specific(self, node):
        new_shape = simpledialog.askstring("Изменить форму узла", f"Введите новую форму для узла '{node}' (например, o, s, ^):")
        if new_shape and new_shape in self.node_shapes:
            self.current_graph.nodes[node]['shape'] = new_shape
            self.log_message(f"Форма узла '{node}' изменена на '{new_shape}'.")
            self.draw_graph()
            self.save_settings()
        else:
            self.log_message(f"Некорректная форма '{new_shape}' для узла '{node}'.")

    # Дополнительные методы могут быть добавлены здесь...

    # Новый метод для изменения цвета ребра
    def change_edge_color(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        if not self.selected_edges:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранных ребер", "Пожалуйста, выберите ребра для изменения цвета.")
            self.log_message("Нет выбранных ребер для изменения цвета.")
            return
        color = colorchooser.askcolor(title="Выберите цвет для ребер")[1]
        if color:
            if self.is_valid_color(color):
                for edge in self.selected_edges:
                    if edge in self.current_graph.edges:
                        self.current_graph.edges[edge]['color'] = color
                        self.log_message(f"Ребро '{edge[0]}' -> '{edge[1]}' окрашено в '{color}'.")
                self.draw_graph()
                self.save_settings()
            else:
                if self.master.winfo_exists():
                    messagebox.showwarning("Некорректный цвет", "Введен некорректный цвет.")
                self.log_message("Введен некорректный цвет.")

    def transform_to_tree_menu(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        if isinstance(self.current_graph, nx.DiGraph):
            if self.master.winfo_exists():
                messagebox.showwarning("Ограничение", "Преобразование в дерево доступно только для неориентированных графов.")
            self.log_message("Преобразование в дерево доступно только для неориентированных графов.")
            return
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Бинарное дерево", command=self.transform_to_binary_tree)
        menu.add_command(label="Обычное дерево", command=self.transform_to_ordinary_tree)
        try:
            menu.tk_popup(int(self.master.winfo_pointerx()), int(self.master.winfo_pointery()))
        finally:
            menu.grab_release()

    def transform_to_binary_tree(self):
        if self.current_graph.is_directed():
            self.log_message("Преобразование в дерево возможно только для неориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Преобразование в дерево возможно только для неориентированных графов.")
            return
        try:
            # Используем алгоритм построения минимального остовного дерева
            tree = nx.minimum_spanning_tree(self.current_graph)
            self.current_graph = tree
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Граф преобразован в бинарное дерево.")
            if self.master.winfo_exists():
                messagebox.showinfo("Преобразование", "Граф преобразован в бинарное дерево.")
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при преобразовании в дерево: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось преобразовать в дерево: {e}")

    def transform_to_ordinary_tree(self):
        if self.current_graph.is_directed():
            self.log_message("Преобразование в дерево возможно только для неориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Преобразование в дерево возможно только для неориентированных графов.")
            return
        try:
            # Проверяем, является ли граф связным
            if not nx.is_connected(self.current_graph):
                self.log_message("Граф не связен. Невозможно преобразовать в дерево.")
                if self.master.winfo_exists():
                    messagebox.showwarning("Ошибка", "Граф не связен. Невозможно преобразовать в дерево.")
                return
            # Используем алгоритм построения минимального остовного дерева
            tree = nx.minimum_spanning_tree(self.current_graph)
            self.current_graph = tree
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Граф преобразован в обычное дерево.")
            if self.master.winfo_exists():
                messagebox.showinfo("Преобразование", "Граф преобразован в обычное дерево.")
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при преобразовании в дерево: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось преобразовать в дерево: {e}")

    # Новый метод для вывода матрицы инцидентности и проверки дерева
    def incidence_matrix(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        try:
            if isinstance(self.current_graph, nx.DiGraph):
                self.log_message("Матрица инцидентности для ориентированного графа не поддерживается.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Матрица инцидентности", "Матрица инцидентности для ориентированного графа не поддерживается.")
                return
            matrix = nx.incidence_matrix(self.current_graph).todense()
            is_tree = nx.is_tree(self.current_graph)
            info = (
                f"Матрица инцидентности:\n{matrix}\n\n"
                f"Является деревом: {'Да' if is_tree else 'Нет'}"
            )
            self.log_message(info)
            if self.master.winfo_exists():
                messagebox.showinfo("Информация о графе", info)
        except Exception as e:
            self.log_message(f"Ошибка при создании матрицы инцидентности: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось создать матрицу инцидентности: {e}")

    # Метод для поиска всех путей (маршрутов) между двумя узлами
    def find_all_paths(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        start = simpledialog.askstring("Все пути", "Введите начальный узел:")
        end = simpledialog.askstring("Все пути", "Введите конечный узел:")
        if not start or not end:
            self.log_message("Не введены начальный или конечный узел.")
            return
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            paths = list(nx.all_simple_paths(self.current_graph, source=start, target=end))
            if paths:
                paths_str = "\n".join([str(path) for path in paths])
                self.log_message(f"Все пути от '{start}' до '{end}':\n{paths_str}")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Все пути от '{start}' до '{end}':\n{paths_str}")
            else:
                self.log_message(f"Пути между '{start}' и '{end}' не найдены.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Пути между '{start}' и '{end}' не найдены.")
        except Exception as e:
            self.log_message(f"Ошибка при поиске путей: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось найти пути: {e}")

    # Метод для вычисления расстояния между двумя узлами
    def calculate_distance(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        start = simpledialog.askstring("Вычислить расстояние", "Введите начальный узел:")
        end = simpledialog.askstring("Вычислить расстояние", "Введите конечный узел:")
        if not start or not end:
            self.log_message("Не введены начальный или конечный узел.")
            return
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            distance = nx.shortest_path_length(self.current_graph, source=start, target=end)
            self.log_message(f"Расстояние между '{start}' и '{end}': {distance}")
            if self.master.winfo_exists():
                messagebox.showinfo("Расстояние", f"Расстояние между '{start}' и '{end}': {distance}")
        except nx.NetworkXNoPath:
            self.log_message(f"Пути между '{start}' и '{end}' нет.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Пути между '{start}' и '{end}' нет.")
        except nx.NodeNotFound as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Узел не найден: {e}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось вычислить расстояние: {e}")

    # Новый метод для трансформации любого графа в дерево
    def transform_to_binary_tree(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        if self.current_graph.is_directed():
            self.log_message("Трансформация доступна только для неориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Трансформация доступна только для неориентированных графов.")
            return
        try:
            # Преобразуем граф в бинарное дерево с использованием алгоритма поиска в ширину
            tree = nx.bfs_tree(self.current_graph, source=list(self.current_graph.nodes)[0])
            self.current_graph = tree
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Граф преобразован в бинарное дерево.")
            if self.master.winfo_exists():
                messagebox.showinfo("Трансформация", "Граф преобразован в бинарное дерево.")
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при трансформации в бинарное дерево: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось трансформировать в бинарное дерево: {e}")

    # Новый метод для трансформации любого графа в обычное дерево
    def transform_to_ordinary_tree(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        if self.current_graph.is_directed():
            self.log_message("Трансформация доступна только для неориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Трансформация доступна только для неориентированных графов.")
            return
        try:
            if not nx.is_connected(self.current_graph):
                self.log_message("Граф не связен. Невозможно преобразовать в дерево.")
                if self.master.winfo_exists():
                    messagebox.showwarning("Ошибка", "Граф не связен. Невозможно преобразовать в дерево.")
                return
            tree = nx.minimum_spanning_tree(self.current_graph)
            self.current_graph = tree
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Граф преобразован в обычное дерево.")
            if self.master.winfo_exists():
                messagebox.showinfo("Трансформация", "Граф преобразован в обычное дерево.")
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при трансформации в обычное дерево: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось трансформировать в обычное дерево: {e}")

    # Новый метод для вывода матрицы инцидентности и проверки дерева
    def incidence_matrix_extended(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        try:
            if isinstance(self.current_graph, nx.DiGraph):
                self.log_message("Матрица инцидентности для ориентированного графа не поддерживается.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Матрица инцидентности", "Матрица инцидентности для ориентированного графа не поддерживается.")
                return
            matrix = nx.incidence_matrix(self.current_graph).todense()
            is_tree = nx.is_tree(self.current_graph)
            info = (
                f"Матрица инцидентности:\n{matrix}\n\n"
                f"Является деревом: {'Да' if is_tree else 'Нет'}"
            )
            self.log_message(info)
            if self.master.winfo_exists():
                messagebox.showinfo("Информация о графе", info)
        except Exception as e:
            self.log_message(f"Ошибка при создании матрицы инцидентности: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось создать матрицу инцидентности: {e}")

    # Метод для поиска всех путей между двумя узлами
    def find_all_paths(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        start = simpledialog.askstring("Все пути", "Введите начальный узел:")
        end = simpledialog.askstring("Все пути", "Введите конечный узел:")
        if not start or not end:
            self.log_message("Не введены начальный или конечный узел.")
            return
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            paths = list(nx.all_simple_paths(self.current_graph, source=start, target=end))
            if paths:
                paths_str = "\n".join([str(path) for path in paths])
                self.log_message(f"Все пути от '{start}' до '{end}':\n{paths_str}")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Все пути от '{start}' до '{end}':\n{paths_str}")
            else:
                self.log_message(f"Пути между '{start}' и '{end}' не найдены.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Пути между '{start}' и '{end}' не найдены.")
        except Exception as e:
            self.log_message(f"Ошибка при поиске путей: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось найти пути: {e}")

    # Метод для вычисления расстояния между двумя узлами
    def calculate_distance(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        start = simpledialog.askstring("Вычислить расстояние", "Введите начальный узел:")
        end = simpledialog.askstring("Вычислить расстояние", "Введите конечный узел:")
        if not start or not end:
            self.log_message("Не введены начальный или конечный узел.")
            return
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            distance = nx.shortest_path_length(self.current_graph, source=start, target=end)
            self.log_message(f"Расстояние между '{start}' и '{end}': {distance}")
            if self.master.winfo_exists():
                messagebox.showinfo("Расстояние", f"Расстояние между '{start}' и '{end}': {distance}")
        except nx.NetworkXNoPath:
            self.log_message(f"Пути между '{start}' и '{end}' нет.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Пути между '{start}' и '{end}' нет.")
        except nx.NodeNotFound as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Узел не найден: {e}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось вычислить расстояние: {e}")

    # Метод для трансформации любого графа в бинарное дерево
    def transform_to_binary_tree(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        if self.current_graph.is_directed():
            self.log_message("Трансформация доступна только для неориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Трансформация доступна только для неориентированных графов.")
            return
        try:
            # Преобразуем граф в бинарное дерево с использованием алгоритма поиска в ширину
            tree = nx.bfs_tree(self.current_graph, source=list(self.current_graph.nodes)[0])
            self.current_graph = tree
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Граф преобразован в бинарное дерево.")
            if self.master.winfo_exists():
                messagebox.showinfo("Трансформация", "Граф преобразован в бинарное дерево.")
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при трансформации в бинарное дерево: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось трансформировать в бинарное дерево: {e}")

    # Метод для трансформации любого графа в обычное дерево
    def transform_to_ordinary_tree(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        if self.current_graph.is_directed():
            self.log_message("Трансформация доступна только для неориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Трансформация доступна только для неориентированных графов.")
            return
        try:
            if not nx.is_connected(self.current_graph):
                self.log_message("Граф не связен. Невозможно преобразовать в дерево.")
                if self.master.winfo_exists():
                    messagebox.showwarning("Ошибка", "Граф не связен. Невозможно преобразовать в дерево.")
                return
            tree = nx.minimum_spanning_tree(self.current_graph)
            self.current_graph = tree
            graph_name = self.get_current_graph_name()
            if graph_name:
                self.graphs[graph_name] = self.current_graph
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.draw_graph()
            self.log_message("Граф преобразован в обычное дерево.")
            if self.master.winfo_exists():
                messagebox.showinfo("Трансформация", "Граф преобразован в обычное дерево.")
            self.save_settings()
        except Exception as e:
            self.log_message(f"Ошибка при трансформации в обычное дерево: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось трансформировать в обычное дерево: {e}")

    # Метод для вывода матрицы инцидентности и проверки дерева
    def graph_info_extended(self):
        if self.current_graph is None:
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф сначала.")
            self.log_message("Нет выбранного графа.")
            return
        num_nodes = self.current_graph.number_of_nodes()
        num_edges = self.current_graph.number_of_edges()
        degrees = dict(self.current_graph.degree())
        is_tree = nx.is_tree(self.current_graph) if not isinstance(self.current_graph, nx.DiGraph) else False
        if not isinstance(self.current_graph, nx.DiGraph):
            incidence_matrix = nx.incidence_matrix(self.current_graph).todense()
        else:
            incidence_matrix = "Матрица инцидентности для ориентированного графа не поддерживается."

        info = (
            f"Узлы: {num_nodes}\n"
            f"Ребра: {num_edges}\n"
            f"Степени узлов: {degrees}\n"
            f"Является деревом: {'Да' if is_tree else 'Нет'}\n"
            f"Матрица инцидентности:\n{incidence_matrix}"
        )
        self.log_message(info)
        if self.master.winfo_exists():
            messagebox.showinfo("Информация о графе", info)

    # Метод для поиска всех путей между двумя узлами
    def find_all_paths(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        start = simpledialog.askstring("Все пути", "Введите начальный узел:")
        end = simpledialog.askstring("Все пути", "Введите конечный узел:")
        if not start or not end:
            self.log_message("Не введены начальный или конечный узел.")
            return
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            paths = list(nx.all_simple_paths(self.current_graph, source=start, target=end))
            if paths:
                paths_str = "\n".join([str(path) for path in paths])
                self.log_message(f"Все пути от '{start}' до '{end}':\n{paths_str}")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Все пути от '{start}' до '{end}':\n{paths_str}")
            else:
                self.log_message(f"Пути между '{start}' и '{end}' не найдены.")
                if self.master.winfo_exists():
                    messagebox.showinfo("Все пути", f"Пути между '{start}' и '{end}' не найдены.")
        except Exception as e:
            self.log_message(f"Ошибка при поиске путей: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось найти пути: {e}")

    # Метод для вычисления расстояния между двумя узлами
    def calculate_distance(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        start = simpledialog.askstring("Вычислить расстояние", "Введите начальный узел:")
        end = simpledialog.askstring("Вычислить расстояние", "Введите конечный узел:")
        if not start or not end:
            self.log_message("Не введены начальный или конечный узел.")
            return
        if start not in self.current_graph or end not in self.current_graph:
            self.log_message("Одного или обоих узлов не существует.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", "Одного или обоих узлов не существует.")
            return
        try:
            distance = nx.shortest_path_length(self.current_graph, source=start, target=end)
            self.log_message(f"Расстояние между '{start}' и '{end}': {distance}")
            if self.master.winfo_exists():
                messagebox.showinfo("Расстояние", f"Расстояние между '{start}' и '{end}': {distance}")
        except nx.NetworkXNoPath:
            self.log_message(f"Пути между '{start}' и '{end}' нет.")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Пути между '{start}' и '{end}' нет.")
        except nx.NodeNotFound as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Узел не найден: {e}")
        except Exception as e:
            self.log_message(f"Ошибка: {e}")
            if self.master.winfo_exists():
                messagebox.showerror("Ошибка", f"Не удалось вычислить расстояние: {e}")

    # Метод для нахождения всех Эйлеровых циклов
    def all_eulerian_cycles(self):
        if self.current_graph is None:
            self.log_message("Нет выбранного графа.")
            if self.master.winfo_exists():
                messagebox.showwarning("Нет выбранного графа", "Пожалуйста, выберите граф.")
            return
        if isinstance(self.current_graph, nx.DiGraph):
            self.log_message("Эйлеровы циклы не поддерживаются для ориентированных графов.")
            if self.master.winfo_exists():
                messagebox.showwarning("Ошибка", "Эйлеровы циклы не поддерживаются для ориентированных графов.")
            return
        if nx.is_eulerian(self.current_graph):
            cycles = list(nx.eulerian_circuit(self.current_graph))
            cycles_str = "\n".join([str(cycle) for cycle in cycles])
            self.log_message(f"Эйлеровы циклы: {cycles_str}")
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеровы циклы", f"Эйлеровы циклы:\n{cycles_str}")
        else:
            self.log_message("В графе нет Эйлеровых циклов.")
            if self.master.winfo_exists():
                messagebox.showinfo("Эйлеровы циклы", "В графе нет Эйлеровых циклов.")  