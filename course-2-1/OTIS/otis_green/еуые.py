import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
from tkinter.colorchooser import askcolor
import pickle

class GraphEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Editor")
        self.graphs = {}
        self.current_graph = None
        self.node_positions = {}

        self.root.configure(bg="#f0f0f0")

        self.setup_ui()

    def setup_ui(self):
        
        top_frame = ttk.Frame(self.root, padding=10, style="TFrame")
        top_frame.pack(side=tk.TOP, fill=tk.X)

        
        style = ttk.Style()
        style.configure("TButton",
                        background="#4CAF50",  
                        foreground="white",  
                        font=("Arial", 10, "bold"),
                        padding=10)

        
        button_texts = [
            ("Создать граф", self.create_graph), ("Удалить граф", self.delete_graph),
            ("Сохранить граф", self.save_graph), ("Загрузить граф", self.load_graph),
            ("Удалить узел", self.delete_node), ("Добавить дугу", self.add_edge),
            ("Удалить дугу", self.delete_edge), ("Окрасить узел", self.color_node),
            ("Окрасить дугу", self.color_edge), ("Информация о графе", self.graph_info),
            ("Найти эйлеров цикл", self.euler_cycle), ("Все пути", self.all_paths),
            ("Кратчайший путь", self.shortest_path), ("Расстояние между узлами", self.compute_distance),
            ("Привести к планарному", self.make_planar)
        ]

        for i, (text, command) in enumerate(button_texts):
            button = ttk.Button(top_frame, text=text, command=command)
            button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

        
        self.canvas = tk.Canvas(self.root, bg="white", bd=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        
        self.canvas.bind("<Button-1>", self.canvas_click)

    def create_graph(self):
        name = simpledialog.askstring("Имя графа", "Введите имя графа:")
        if name:
            if name in self.graphs:
                messagebox.showerror("Ошибка", "Граф с таким именем уже существует.")
                return
            self.graphs[name] = nx.MultiDiGraph()
            self.node_positions[name] = {}
            self.current_graph = name
            self.draw_graph()

    def delete_graph(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        del self.graphs[self.current_graph]
        del self.node_positions[self.current_graph]
        self.current_graph = None
        self.canvas.delete("all")

    def save_graph(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        file = simpledialog.askstring("Сохранить граф", "Введите имя файла:")
        if file:
            with open(file, 'wb') as f:
                pickle.dump(self.graphs[self.current_graph], f)
            messagebox.showinfo("Успех", "Граф сохранен.")

    def load_graph(self):
        file = simpledialog.askstring("Загрузить граф", "Введите имя файла:")
        if file:
            try:
                with open(file, 'rb') as f:
                    graph = pickle.load(f)
                name = simpledialog.askstring("Имя графа", "Введите имя для загруженного графа:")
                if name in self.graphs:
                    messagebox.showerror("Ошибка", "Граф с таким именем уже существует.")
                    return
                self.graphs[name] = graph
                self.node_positions[name] = {}
                self.current_graph = name
                self.draw_graph()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить граф: {e}")

    def delete_node(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        name = simpledialog.askstring("Имя узла", "Введите имя узла для удаления:")
        if name:
            graph = self.graphs[self.current_graph]
            if name not in graph:
                messagebox.showerror("Ошибка", "Узел не найден.")
                return
            graph.remove_node(name)
            del self.node_positions[self.current_graph][name]
            self.draw_graph()

    def add_edge(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        source = simpledialog.askstring("Источник", "Введите имя исходного узла:")
        target = simpledialog.askstring("Цель", "Введите имя целевого узла:")
        if source and target:
            graph = self.graphs[self.current_graph]
            if source not in graph or target not in graph:
                messagebox.showerror("Ошибка", "Один или оба узла не найдены.")
                return
            graph.add_edge(source, target)
            self.draw_graph()

    def delete_edge(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        source = simpledialog.askstring("Источник", "Введите имя исходного узла:")
        target = simpledialog.askstring("Цель", "Введите имя целевого узла:")
        if source and target:
            graph = self.graphs[self.current_graph]
            if not graph.has_edge(source, target):
                messagebox.showerror("Ошибка", "Дуга не найдена.")
                return
            graph.remove_edge(source, target)
            self.draw_graph()

    def color_node(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        node = simpledialog.askstring("Узел", "Введите имя узла:")
        if node:
            graph = self.graphs[self.current_graph]
            if node not in graph:
                messagebox.showerror("Ошибка", "Узел не найден.")
                return
            color = askcolor()[1]
            if color:
                graph.nodes[node]['color'] = color
                self.draw_graph()

    def color_edge(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        source = simpledialog.askstring("Источник", "Введите имя исходного узла:")
        target = simpledialog.askstring("Цель", "Введите имя целевого узла:")
        if source and target:
            graph = self.graphs[self.current_graph]
            if not graph.has_edge(source, target):
                messagebox.showerror("Ошибка", "Дуга не найдена.")
                return
            color = askcolor()[1]
            if color:
                for edge in graph.edges(source, target):
                    graph.edges[edge]['color'] = color
                self.draw_graph()

    def graph_info(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        graph = self.graphs[self.current_graph]
        nodes = graph.number_of_nodes()
        edges = graph.number_of_edges()
        messagebox.showinfo("Информация о графе", f"Узлов: {nodes}, Дуг: {edges}")

    def euler_cycle(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        graph = self.graphs[self.current_graph]
        try:
            cycle = list(nx.eulerian_circuit(graph))
            messagebox.showinfo("Эйлеров цикл", f"Цикл: {cycle}")
        except nx.NetworkXError:
            messagebox.showerror("Ошибка", "Граф не содержит эйлерова цикла.")

    def all_paths(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        source = simpledialog.askstring("Источник", "Введите имя исходного узла:")
        target = simpledialog.askstring("Цель", "Введите имя целевого узла:")
        if source and target:
            graph = self.graphs[self.current_graph]
            if source not in graph or target not in graph:
                messagebox.showerror("Ошибка", "Один или оба узла не найдены.")
                return
            paths = list(nx.all_simple_paths(graph, source, target))
            messagebox.showinfo("Все пути", f"Пути: {paths}")

    def shortest_path(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        source = simpledialog.askstring("Источник", "Введите имя исходного узла:")
        target = simpledialog.askstring("Цель", "Введите имя целевого узла:")
        if source and target:
            graph = self.graphs[self.current_graph]
            if source not in graph or target not in graph:
                messagebox.showerror("Ошибка", "Один или оба узла не найдены.")
                return
            try:
                path = nx.shortest_path(graph, source, target)
                messagebox.showinfo("Кратчайший путь", f"Путь: {path}")
            except nx.NetworkXNoPath:
                messagebox.showerror("Ошибка", "Нет пути между узлами.")

    def compute_distance(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        source = simpledialog.askstring("Источник", "Введите имя исходного узла:")
        target = simpledialog.askstring("Цель", "Введите имя целевого узла:")
        if source and target:
            graph = self.graphs[self.current_graph]
            if source not in graph or target not in graph:
                messagebox.showerror("Ошибка", "Один или оба узла не найдены.")
                return
            try:
                distance = nx.shortest_path_length(graph, source, target)
                messagebox.showinfo("Расстояние", f"Расстояние между узлами: {distance}")
            except nx.NetworkXNoPath:
                messagebox.showerror("Ошибка", "Нет пути между узлами.")

    def make_planar(self):
        if not self.current_graph:
            messagebox.showerror("Ошибка", "Нет выбранного графа.")
            return
        graph = self.graphs[self.current_graph]
        
        # Проверка, является ли граф планарным
        planar, _ = nx.check_planarity(graph)
        
        if planar:
            messagebox.showinfo("Планарность", "Граф уже является планарным.")
            return
        
        edges_to_remove = list(graph.edges())
        removed_edges = []
        
        for edge in edges_to_remove:
            graph.remove_edge(*edge)
            planar, _ = nx.check_planarity(graph)
            if planar:
                removed_edges.append(edge)
                break
            else:
                graph.add_edge(*edge)  

        if planar:
            messagebox.showinfo("Планарность", f"Граф стал планарным после удаления рёбер: {removed_edges}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сделать граф планарным.")

    def draw_graph(self):
        if not self.current_graph:
            return
        self.canvas.delete("all")
        graph = self.graphs[self.current_graph]
        pos = self.node_positions[self.current_graph]
        for node, (x, y) in pos.items():
            color = graph.nodes[node].get('color', 'lightblue')
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline="black")
            self.canvas.create_text(x, y, text=node)
        for u, v, data in graph.edges(data=True):
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            color = data.get('color', 'black')
            self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color)

    def canvas_click(self, event):
        if not self.current_graph:
            return
        x, y = event.x, event.y
        name = simpledialog.askstring("Имя узла", "Введите имя узла:")
        if name:
            graph = self.graphs[self.current_graph]
            if name in graph:
                messagebox.showerror("Ошибка", "Узел с таким именем уже существует.")
                return
            graph.add_node(name)
            self.node_positions[self.current_graph][name] = (x, y)
            self.draw_graph()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()
