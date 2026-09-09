import sys
from PyQt5.QtWidgets import QApplication
from app.main_menu import MainMenu
from source.file_operations import init_data_dir

def main():
    init_data_dir()  # Инициализация папок
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()