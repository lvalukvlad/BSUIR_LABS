from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QMessageBox,
                             QAction, QFileDialog, QMenu)
from PyQt5.QtCore import pyqtSignal
from components.header import Header
from components.list_of_tournaments import TournamentList
from components.pagination import Pagination
from source.get_tournaments import load_tournaments
from source.save_tournaments import save_tournaments
from source.file_operations import get_open_filename


class MainMenu(QMainWindow):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление турнирами")
        self.resize(1000, 700)
        self.tournaments = []
        self.current_file = None

        self._setup_ui()
        self._setup_actions()

    def _setup_ui(self):
        self.header = Header()
        self.tournament_list = TournamentList(self.tournaments)
        self.pagination = Pagination(len(self.tournaments))

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.header)
        layout.addWidget(self.tournament_list)
        layout.addWidget(self.pagination)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
        self.data_changed.connect(self._update_display)

    def _setup_actions(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        # Меню Турниры
        tournament_menu = menubar.addMenu("Турниры")
        add_action = QAction("Добавить турнир", self)
        add_action.triggered.connect(self._show_add_dialog)
        tournament_menu.addAction(add_action)

        find_action = QAction("Найти турниры", self)
        find_action.triggered.connect(self._show_find_dialog)
        tournament_menu.addAction(find_action)

        delete_action = QAction("Удалить турниры", self)
        delete_action.triggered.connect(self._show_delete_dialog)
        tournament_menu.addAction(delete_action)

    def _update_display(self):
        self.tournament_list.update_data(self.tournaments)
        self.pagination.update_total(len(self.tournaments))

    def _open_file(self):
        filename = get_open_filename(self)
        if filename:
            try:
                self.tournaments = load_tournaments(filename)
                self.current_file = filename
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _save_file(self):
        if not self.current_file:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить файл турниров",
                "",
                "XML Files (*.xml)"
            )
            if not filename:
                return
            self.current_file = filename

        try:
            save_tournaments(self.current_file, self.tournaments)
            QMessageBox.information(self, "Успех", "Файл успешно сохранен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")