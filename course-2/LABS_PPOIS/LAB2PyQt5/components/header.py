from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class Header(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Система управления турнирами")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 1px solid #ccc;
        """)