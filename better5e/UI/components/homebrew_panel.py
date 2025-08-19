from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox

from better5e.UI.components.section_header import SectionHeader
from better5e.UI.core.style.theme import add_shadow
from better5e.UI.core.style.tokens import gutter
from better5e.UI.pages.feature_form_page import FeatureFormPage


class HomebrewPanel(QWidget):
    """Vertical list of buttons for creating homebrew objects."""

    openHomebrew = pyqtSignal(str)

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(gutter(), gutter(), gutter(), gutter())
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
            add_shadow(btn)
            btn.clicked.connect(lambda _, k=kind: self._on_create(k))
            layout.addWidget(btn)

        layout.addStretch(1)

    def _on_create(self, kind: str) -> None:
        if kind == "feature":
            self.app.push(FeatureFormPage(self.app))
            return
        if self.receivers(self.openHomebrew) > 0:
            self.openHomebrew.emit(kind)
        else:  # pragma: no cover
            QMessageBox.information(self, "Not Implemented", f"Creation of {kind} not implemented.")
