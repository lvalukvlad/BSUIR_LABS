from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel,
                             QSpinBox, QComboBox, QPushButton)
from PyQt5.QtCore import pyqtSignal


class Pagination(QWidget):
    page_changed = pyqtSignal(int)
    items_per_page_changed = pyqtSignal(int)

    def __init__(self, total_items=0, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.items_per_page = 10
        self.total_items = total_items
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()

        self.first_btn = QPushButton("<<")
        self.prev_btn = QPushButton("<")
        self.next_btn = QPushButton(">")
        self.last_btn = QPushButton(">>")

        self.page_label = QLabel("Страница:")
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.of_label = QLabel(f"из {self.total_pages}")

        self.items_label = QLabel("Записей на странице:")
        self.items_combo = QComboBox()
        self.items_combo.addItems(["5", "10", "20", "50", "Все"])
        self.items_combo.setCurrentText("10")

        layout.addWidget(self.first_btn)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.page_label)
        layout.addWidget(self.page_spin)
        layout.addWidget(self.of_label)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.last_btn)
        layout.addStretch()
        layout.addWidget(self.items_label)
        layout.addWidget(self.items_combo)

        self.setLayout(layout)

        self.first_btn.clicked.connect(self.go_to_first)
        self.prev_btn.clicked.connect(self.go_to_prev)
        self.next_btn.clicked.connect(self.go_to_next)
        self.last_btn.clicked.connect(self.go_to_last)
        self.page_spin.valueChanged.connect(self.change_page)
        self.items_combo.currentTextChanged.connect(self.change_items_per_page)

        self.update_controls()

    def update_total(self, total_items):
        self.total_items = total_items
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        self.of_label.setText(f"из {self.total_pages}")
        self.page_spin.setMaximum(self.total_pages)
        self.update_controls()

    def update_controls(self):
        self.first_btn.setEnabled(self.current_page > 1)
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < self.total_pages)
        self.last_btn.setEnabled(self.current_page < self.total_pages)
        self.page_spin.setValue(self.current_page)

    def go_to_first(self):
        self.current_page = 1
        self.page_changed.emit(self.current_page)
        self.update_controls()

    def go_to_prev(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.page_changed.emit(self.current_page)
            self.update_controls()

    def go_to_next(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_changed.emit(self.current_page)
            self.update_controls()

    def go_to_last(self):
        self.current_page = self.total_pages
        self.page_changed.emit(self.current_page)
        self.update_controls()

    def change_page(self, page):
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.page_changed.emit(self.current_page)
            self.update_controls()

    def change_items_per_page(self, text):
        if text == "Все":
            self.items_per_page = -1
        else:
            self.items_per_page = int(text)

        self.total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        self.of_label.setText(f"из {self.total_pages}")
        self.page_spin.setMaximum(self.total_pages)
        self.current_page = 1

        self.items_per_page_changed.emit(self.items_per_page)
        self.page_changed.emit(self.current_page)
        self.update_controls()