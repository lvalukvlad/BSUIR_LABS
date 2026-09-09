class FilterBar(QWidget):
    def __init__(self):
        super().__init__()
        self.sport_filter.addItems(["Все"] + self._load_sports())
        self.sport_filter.currentTextChanged.connect(self._emit_filter)