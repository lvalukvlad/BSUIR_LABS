from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox
from components.create_input_form import TournamentInputForm
from source.validate_create_tournament import validate_tournament_data


class CreateTournamentMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление нового турнира")
        self.setFixedSize(500, 400)

        self.form = TournamentInputForm()
        self.submit_btn = QPushButton("Сохранить")
        self.submit_btn.clicked.connect(self._handle_submit)

        layout = QVBoxLayout()
        layout.addWidget(self.form)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

    def _handle_submit(self):
        data = self.form.get_data()
        errors = validate_tournament_data(data)

        if errors:
            QMessageBox.warning(self, "Ошибки ввода", "\n".join(errors))
        else:
            self.accept()
            return data