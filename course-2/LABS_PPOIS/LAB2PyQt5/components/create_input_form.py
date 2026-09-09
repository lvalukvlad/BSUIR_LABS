from PyQt5.QtWidgets import (QWidget, QFormLayout, QLineEdit,
                             QDateEdit, QComboBox, QDoubleSpinBox)
from PyQt5.QtCore import QDate


class TournamentInputForm(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.date_input = QDateEdit(QDate.currentDate())
        self.sport_input = QComboBox()
        self.winner_input = QLineEdit()
        self.prize_input = QDoubleSpinBox()
        self.prize_input.setMaximum(100000000)
        self.prize_input.setPrefix("$ ")

        self.sport_input.addItems([
            "Футбол", "Теннис", "Баскетбол",
            "Шахматы", "Плавание", "Легкая атлетика"
        ])

        layout.addRow("Название турнира:", self.name_input)
        layout.addRow("Дата проведения:", self.date_input)
        layout.addRow("Вид спорта:", self.sport_input)
        layout.addRow("ФИО победителя:", self.winner_input)
        layout.addRow("Призовой фонд:", self.prize_input)

        self.setLayout(layout)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "date": self.date_input.date().toPyDate(),
            "sport_type": self.sport_input.currentText(),
            "winner_name": self.winner_input.text(),
            "prize_fund": self.prize_input.value()
        }