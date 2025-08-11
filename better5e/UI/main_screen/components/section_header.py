from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout


class SectionHeader(QWidget):
    """Header with title and a 'See All >' control."""

    seeAll = pyqtSignal()

    def __init__(self, title: str) -> None:
        super().__init__()
        self.setProperty("class", "SectionHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel(title))
        layout.addStretch()

        button = QPushButton("See All >")
        button.setProperty("class", "ghost")
        layout.addWidget(button)
        button.clicked.connect(self.seeAll.emit)
        self.button = button
