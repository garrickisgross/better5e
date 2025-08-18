from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout

from better5e.UI.style.theme import add_shadow


class CardGrid(QWidget):
    """Display placeholder cards in a three-up grid."""

    def __init__(self, titles: list[str]) -> None:
        super().__init__()
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(12)

        for i, title in enumerate(titles):
            card = QFrame()
            card.setObjectName("Card")
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card.setMinimumSize(200, 220)
            add_shadow(card)
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(
                QLabel(title, alignment=Qt.AlignmentFlag.AlignCenter)
            )
            row, col = divmod(i, 3)
            layout.addWidget(card, row, col)
