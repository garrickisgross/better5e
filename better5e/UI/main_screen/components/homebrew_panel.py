from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.style.theme import add_shadow


class HomebrewPanel(QWidget):
    """Vertical list of buttons for creating homebrew objects."""

    openHomebrew = pyqtSignal(str)

    def __init__(self, app) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = SectionHeader("Homebrew")
        header.button.hide()
        layout.addWidget(header)

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
            # Buttons are placeholders and do not trigger actions
            add_shadow(btn)
            layout.addWidget(btn)

        layout.addStretch(1)
