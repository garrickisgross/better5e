from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.style.theme import add_shadow
from better5e.UI.homebrew.feature_create_page import FeatureCreatePage


class HomebrewPanel(QWidget):
    """Vertical list of buttons for creating homebrew objects."""

    openHomebrew = pyqtSignal(str)

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
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
            if kind == "feature":
                btn.clicked.connect(lambda _=False: self.app.push(FeatureCreatePage(self.app)))
            else:
                btn.clicked.connect(lambda _=False, k=kind: self.openHomebrew.emit(k))
            add_shadow(btn)
            layout.addWidget(btn)

        layout.addStretch(1)
