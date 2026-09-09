from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox,
                             QLineEdit, QPushButton, QMessageBox)


class DeleteTournamentMenu(QDialog):
    def __init__(self, tournaments, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление турниров")
        self.tournaments = tournaments
        self.setFixedSize(400, 200)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.field_combo = QComboBox()
        self.field_combo.addItems([
            "Название турнира",
            "Дата проведения",
            "Вид спорта",
            "ФИО победителя"
        ])

        self.value_input = QLineEdit()
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self._confirm_deletion)

        form_layout.addRow("Поле для удаления:", self.field_combo)
        form_layout.addRow("Значение:", self.value_input)
        form_layout.addRow(self.delete_btn)

        layout.addLayout(form_layout)
        self.setLayout(layout)

    def _confirm_deletion(self):
        field_map = {
            "Название турнира": "name",
            "Дата проведения": "date",
            "Вид спорта": "sport_type",
            "ФИО победителя": "winner_name"
        }

        field = field_map[self.field_combo.currentText()]
        value = self.value_input.text().strip()

        if not value:
            QMessageBox.warning(self, "Ошибка", "Введите значение для поиска")
            return

        # Подсчет совпадений
        matches = [t for t in self.tournaments
                   if str(getattr(t, field)).lower().find(value.lower()) != -1]

        if not matches:
            QMessageBox.information(self, "Результат", "Совпадений не найдено")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Найдено {len(matches)} турниров. Удалить?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for tour in matches:
                self.tournaments.remove(tour)
            self.accept()
            QMessageBox.information(self, "Успех", "Турниры удалены")