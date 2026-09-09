# main.py
import tkinter as tk
from main_view import MainView

def main():
    root = tk.Tk()
    root.title("Графовый Редактор")
    root.geometry("1200x800")
    app = MainView(master=root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()