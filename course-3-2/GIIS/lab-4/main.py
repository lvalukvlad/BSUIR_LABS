import tkinter as tk
import state
from ui import run as ui_run


def main():
    state.root = tk.Tk()
    ui_run()


if __name__ == "__main__":
    main()
