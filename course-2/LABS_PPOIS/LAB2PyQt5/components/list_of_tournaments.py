from PyQt5.QtWidgets import QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt


class TournamentList(QTableView):
    def __init__(self, tournaments, parent=None):
        super().__init__(parent)
        self.model = TournamentTableModel(tournaments)
        self.setModel(self.model)
        self.resizeColumnsToContents()

    def update_data(self, tournaments):
        self.model.update_data(tournaments)
        self.resizeColumnsToContents()


class TournamentTableModel(QAbstractTableModel):
    def __init__(self, tournaments):
        super().__init__()
        self.tournaments = tournaments
        self.headers = [
            "Название", "Дата", "Вид спорта",
            "Победитель", "Призовой фонд", "Заработок"
        ]

    def update_data(self, tournaments):
        self.beginResetModel()
        self.tournaments = tournaments
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self.tournaments)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        tour = self.tournaments[index.row()]

        if role == Qt.DisplayRole:
            return [
                tour.name,
                tour.date.strftime("%d.%m.%Y"),
                tour.sport_type,
                tour.winner_name,
                f"${tour.prize_fund:,.2f}",
                f"${tour.winner_earnings:,.2f}"
            ][index.column()]

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None