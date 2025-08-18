from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from better5e.UI.components.section_header import SectionHeader
from better5e.UI.pages.create_background_page import CreateBackgroundPage
from better5e.UI.pages.create_class_page import CreateClassPage
from better5e.UI.pages.create_feature_page import CreateFeaturePage
from better5e.UI.pages.create_item_page import CreateItemPage
from better5e.UI.pages.create_race_page import CreateRacePage
from better5e.UI.pages.create_spell_page import CreateSpellPage
from better5e.UI.pages.create_spellcasting_page import CreateSpellcastingPage
from better5e.UI.pages.create_subclass_page import CreateSubclassPage
from better5e.UI.style.theme import add_shadow


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

        self._pages = {
            "feature": CreateFeaturePage,
            "class": CreateClassPage,
            "subclass": CreateSubclassPage,
            "item": CreateItemPage,
            "spellcasting": CreateSpellcastingPage,
            "spell": CreateSpellPage,
            "race": CreateRacePage,
            "background": CreateBackgroundPage,
        }

        for kind in self._pages.keys():
            btn = QPushButton(f"Create {kind.title()}")
            add_shadow(btn)
            btn.clicked.connect(lambda _, k=kind: self._open(k))
            layout.addWidget(btn)

        layout.addStretch(1)

    def _open(self, kind: str) -> None:
        self.openHomebrew.emit(kind)
        page_cls = self._pages.get(kind)
        if page_cls is not None:
            self.app.push(page_cls(self.app))
