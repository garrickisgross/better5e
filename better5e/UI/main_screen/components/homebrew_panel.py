from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy

from better5e.UI.style.theme import add_shadow


class HomebrewPanel(QWidget):
    """Vertical list of buttons for creating homebrew objects."""

    openHomebrew = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        title = QLabel("Homebrew")
        title.setObjectName("SectionHeader")
        layout.addWidget(title)

        rulesHdr = QLabel("Rules")
        rulesHdr.setProperty("class", "subhead")
        layout.addWidget(rulesHdr)
        rules = [
            ("feature", "Feature", "Custom abilities"),
            ("spellcasting", "Spellcasting", "Magic mechanics"),
        ]
        for kind, text, cap in rules:
            layout.addWidget(self._make_entry(kind, text, cap))

        contentHdr = QLabel("Content")
        contentHdr.setProperty("class", "subhead")
        layout.addWidget(contentHdr)
        content = [
            ("class", "Class", "Character class"),
            ("subclass", "Subclass", "Archetype"),
            ("background", "Background", "Origin story"),
            ("race", "Race", "Playable race"),
            ("item", "Item", "Equipment"),
            ("spell", "Spell", "Magic spell"),
        ]
        for kind, text, cap in content:
            layout.addWidget(self._make_entry(kind, text, cap))

        layout.addStretch(1)

    def _make_entry(self, kind: str, text: str, caption: str) -> QWidget:
        wrap = QWidget()
        col = QVBoxLayout(wrap)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(2)
        btn = QPushButton(f"Create {text}")
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn.clicked.connect(lambda _=False, k=kind: self.openHomebrew.emit(k))
        add_shadow(btn)
        cap = QLabel(caption)
        cap.setWordWrap(False)
        cap.setProperty("class", "caption")
        col.addWidget(btn)
        col.addWidget(cap)
        return wrap
