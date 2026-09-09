
# main_view.py
import tkinter as tk
from graph_editor import GraphEditor

class MainView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.graph_editor = GraphEditor(master=self)
        self.graph_editor.pack(fill=tk.BOTH, expand=True)