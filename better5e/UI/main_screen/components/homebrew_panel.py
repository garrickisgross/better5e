from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.style.theme import add_shadow
from better5e.UI.main_screen.pages import (
    CreateFeaturePage,
    CreateClassPage,
    CreateSubclassPage,
    CreateItemPage,
    CreateSpellcastingPage,
    CreateSpellPage,
    CreateRacePage,
    CreateBackgroundPage,
)


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

        self._factories = {
            "feature": CreateFeaturePage,
            "class": CreateClassPage,
            "subclass": CreateSubclassPage,
            "item": CreateItemPage,
            "spellcasting": CreateSpellcastingPage,
            "spell": CreateSpellPage,
            "race": CreateRacePage,
            "background": CreateBackgroundPage,
        }

        for kind in kinds:
            btn = QPushButton(f"Create {kind.title()}")
            btn.clicked.connect(lambda _=False, k=kind: self._open(k))
            add_shadow(btn)
            layout.addWidget(btn)

        layout.addStretch(1)

    def _open(self, kind: str) -> None:
        """Open a homebrew editor page for *kind*."""
        self.openHomebrew.emit(kind)
        factory = self._factories.get(kind)
        if factory:
            self.app.push(factory(self.app))
