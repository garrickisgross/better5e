from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QFrame,
    QHBoxLayout,
)

from better5e.models.game_object import Action, ActionType


class _ActionCard(QFrame):
    def __init__(self, remove_cb) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.name_edit = QLineEdit()
        top.addWidget(self.name_edit)
        self.type_combo = QComboBox()
        for t in ActionType:
            self.type_combo.addItem(t.name.replace("_", " ").title(), t)
        top.addWidget(self.type_combo)
        rm = QPushButton("Remove")
        rm.clicked.connect(lambda: remove_cb(self))
        top.addWidget(rm)
        layout.addLayout(top)
        self.desc_edit = QTextEdit()
        layout.addWidget(self.desc_edit)

    def to_model(self) -> Action:
        return Action(
            action_type=self.type_combo.currentData(),
            name=self.name_edit.text() or None,
            desc=self.desc_edit.toPlainText() or None,
        )


class ActionsEditor(QWidget):
    """Manage a list of action cards."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.cards_layout = QVBoxLayout()
        layout.addLayout(self.cards_layout)
        add_btn = QPushButton("Add Action")
        add_btn.clicked.connect(self.add_card)
        layout.addWidget(add_btn)
        self._cards: list[_ActionCard] = []

    def add_card(self) -> None:
        card = _ActionCard(self.remove_card)
        self._cards.append(card)
        self.cards_layout.addWidget(card)

    def remove_card(self, card: _ActionCard) -> None:
        self._cards.remove(card)
        self.cards_layout.removeWidget(card)
        card.deleteLater()

    def actions(self) -> list[Action]:
        return [c.to_model() for c in self._cards]
