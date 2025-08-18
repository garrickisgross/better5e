from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.style.theme import add_shadow
from better5e.UI.main_screen.create_pages.CreatePage import CreatePage


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
            "Feature",
            "Class",
            "Subclass",
            "Item",
            "Spellcasting",
            "Spell",
            "Race",
            "Background",
        ]

        for kind in kinds:
            btn = QPushButton(f"Create {kind}")
            add_shadow(btn)
            btn.clicked.connect(lambda _=False, k=kind: self._open_create(k))
            layout.addWidget(btn)

        layout.addStretch(1)

    def _open_create(self, kind: str) -> None:
        page = CreatePage(self.app, kind)
        self.app.push(page)
        self.openHomebrew.emit(kind)
