from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from better5e.UI.style.theme import add_shadow


class GridCard(QFrame):
    """Card with hover actions."""

    opened = pyqtSignal(object)
    edited = pyqtSignal(object)

    def __init__(self, title: str, payload=None) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setMinimumSize(220, 200)
        add_shadow(self)
        self.payload = payload

        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        preview = QWidget()
        preview.setObjectName("CardPreview")
        lay.addWidget(preview)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("CardTitle")
        lay.addWidget(title_lbl)

        actions_w = QWidget()
        actions_w.setObjectName("CardActions")
        actions_l = QHBoxLayout(actions_w)
        actions_l.setContentsMargins(0, 0, 0, 0)
        actions_l.setSpacing(6)
        open_btn = QPushButton("Open")
        edit_btn = QPushButton("Edit")
        open_btn.clicked.connect(lambda: self.opened.emit(self.payload))
        edit_btn.clicked.connect(lambda: self.edited.emit(self.payload))
        actions_l.addWidget(open_btn)
        actions_l.addWidget(edit_btn)
        actions_l.addStretch(1)
        lay.addWidget(actions_w)
        actions_w.hide()
        self.actions_w = actions_w
        self.preview = preview

    def enterEvent(self, e) -> None:  # pragma: no cover - UI hover
        self.actions_w.show()
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:  # pragma: no cover - UI hover
        self.actions_w.hide()
        super().leaveEvent(e)

    def resizeEvent(self, e) -> None:  # pragma: no cover - geometry calc
        super().resizeEvent(e)
        w = self.preview.width()
        self.preview.setFixedHeight(int(w * 3 / 4))


class CardGrid(QWidget):
    """Display cards in a responsive grid."""

    def __init__(self, titles: list[str]) -> None:
        super().__init__()
        self._cards: list[GridCard] = []
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)
        self.grid = layout
        if not titles:
            empty = QLabel("No items yet", alignment=Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(empty, 0, 0)
            return
        for title in titles:
            card = GridCard(title, payload=title)
            self._cards.append(card)
        self._reflow()

    def resizeEvent(self, e) -> None:  # pragma: no cover - geometry calc
        super().resizeEvent(e)
        self._reflow()

    def _reflow(self) -> None:
        cols = 2 if self.width() <= 1100 else 3
        for i, card in enumerate(self._cards):
            row, col = divmod(i, cols)
            self.grid.addWidget(card, row, col)

