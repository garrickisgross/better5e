from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class HomebrewPanel(QWidget):
    """Vertical list of buttons for creating homebrew objects."""

    openHomebrew = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        kinds = [
            "feature",
            "class",
            "subclass",
            "item",
            "spellcasting",
            "spell",
            "race",
            "background",
        ]

        for kind in kinds:
            btn = QPushButton(f"Create {kind.title()}")
            btn.clicked.connect(lambda _=False, k=kind: self.openHomebrew.emit(k))
            layout.addWidget(btn)

        layout.addStretch()
