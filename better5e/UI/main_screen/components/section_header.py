from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)


class SectionHeader(QWidget):
    """Header with title and a 'See All >' control."""

    seeAll = pyqtSignal()

    def __init__(self, title: str) -> None:
        super().__init__()
        self.setProperty("class", "SectionHeader")
        self.setObjectName("SectionHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)
        layout.addStretch()

        button = QPushButton("See All >")
        button.setProperty("class", "ghost")
        layout.addWidget(button)
        button.clicked.connect(self.seeAll.emit)
        self.button = button


class Section(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Section")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 12, 0, 0)
        lay.setSpacing(8)

        header = SectionHeader(title)
        lay.addWidget(header)
        self.header = header

        self.body = QVBoxLayout()
        self.body.setSpacing(12)
        lay.addLayout(self.body)
