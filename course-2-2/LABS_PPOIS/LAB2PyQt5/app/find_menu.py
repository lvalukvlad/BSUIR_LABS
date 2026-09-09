from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDateEdit, QComboBox, QPushButton, QGroupBox,
                             QDoubleSpinBox)
from components.list_of_tournaments import TournamentList


class FindTournamentMenu(QDialog):
    def __init__(self, tournaments, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск турниров")
        self.setMinimumSize(700, 600)
        self.tournaments = tournaments

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Форма поиска
        self.search_group = QGroupBox("Критерии поиска")
        search_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.sport_input = QComboBox()
        self.winner_input = QLineEdit()
        self.min_prize = QDoubleSpinBox()
        self.max_prize = QDoubleSpinBox()

        # Настройка элементов
        self.sport_input.addItem("Любой вид спорта")
        sports = {t.sport_type for t in self.tournaments}
        self.sport_input.addItems(sorted(sports))

        self.min_prize.setMaximum(9999999)
        self.min_prize.setPrefix("$ ")
        self.max_prize.setMaximum(9999999)
        self.max_prize.setPrefix("$ ")

        # Добавление в layout
        search_layout.addRow("Название содержит:", self.name_input)
        search_layout.addRow("Дата проведения:", self.date_input)
        search_layout.addRow("Вид спорта:", self.sport_input)
        search_layout.addRow("Победитель содержит:", self.winner_input)
        search_layout.addRow("Призовой фонд от:", self.min_prize)
        search_layout.addRow("Призовой фонд до:", self.max_prize)

        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self._perform_search)
        search_layout.addRow(search_btn)

        self.search_group.setLayout(search_layout)

        # Результаты поиска
        self.results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout()
        self.results_table = TournamentList([])
        results_layout.addWidget(self.results_table)
        self.results_group.setLayout(results_layout)

        # Общий layout
        layout.addWidget(self.search_group)
        layout.addWidget(self.results_group)
        self.setLayout(layout)

    def _perform_search(self):
        criteria = {
            'name': self.name_input.text().strip(),
            'date': self.date_input.date().toPyDate() if self.date_input.date().isValid() else None,
            'sport_type': self.sport_input.currentText() if self.sport_input.currentIndex() > 0 else None,
            'winner_name': self.winner_input.text().strip(),
            'min_prize': self.min_prize.value(),
            'max_prize': self.max_prize.value() if self.max_prize.value() > 0 else float('inf')
        }

        results = []
        for tour in self.tournaments:
            match = True

            # Проверка критериев
            if criteria['name'] and criteria['name'].lower() not in tour.name.lower():
                match = False
            elif criteria['date'] and tour.date != criteria['date']:
                match = False
            elif criteria['sport_type'] and tour.sport_type != criteria['sport_type']:
                match = False
            elif criteria['winner_name'] and criteria['winner_name'].lower() not in tour.winner_name.lower():
                match = False
            elif not (criteria['min_prize'] <= tour.prize_fund <= criteria['max_prize']):
                match = False

            if match:
                results.append(tour)

        self.results_table.update_data(results)