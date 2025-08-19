from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QPushButton,
)

from better5e.UI.core.style.tokens import gutter
from better5e.UI.core.style.theme import add_shadow
from better5e.UI.components.section_header import SectionHeader
from better5e.models.game_object import Action, Rollable, Modifier
from better5e.models.enums import ActionType, Op


class ActionsEditor(QWidget):
    """Widget for editing a list of :class:`Action` objects."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(gutter(), gutter(), gutter(), gutter())
        layout.setSpacing(12)

        self._cards_layout = QVBoxLayout()
        self._cards_layout.setSpacing(12)
        layout.addLayout(self._cards_layout)

        header = SectionHeader("Add Action")
        header.button.hide()
        layout.addWidget(header)

        form = QHBoxLayout()
        form.setSpacing(12)

        self.type_combo = QComboBox()
        for at in ActionType:
            self.type_combo.addItem(at.name.replace("_", " ").title(), at)
        form.addWidget(self.type_combo)

        self.num_input = QSpinBox()
        self.num_input.setMinimum(1)
        self.num_input.setMaximum(100)
        self.num_input.setValue(1)
        form.addWidget(self.num_input)

        self.sides_input = QSpinBox()
        self.sides_input.setMinimum(2)
        self.sides_input.setMaximum(1000)
        self.sides_input.setValue(6)
        form.addWidget(self.sides_input)

        self.mod_input = QSpinBox()
        self.mod_input.setRange(-999, 999)
        self.mod_input.setValue(0)
        form.addWidget(self.mod_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name (optional)")
        form.addWidget(self.name_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Desc (optional)")
        form.addWidget(self.desc_input)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_action)
        form.addWidget(add_btn)

        layout.addLayout(form)
        layout.addStretch(1)

        self._actions: list[Action] = []

    # ------------------------------------------------------------------
    def _notation_for(self, action: Action) -> str:
        if not action.roll:
            return ""
        notation = f"{action.roll.num}d{action.roll.sides}"
        mod = action.roll.modifier.value if action.roll.modifier else 0
        if mod:
            sign = "+" if mod > 0 else "-"
            notation += f" {sign} {abs(mod)}"
        return notation

    def _render_card(self, action: Action) -> None:
        card = QFrame()
        card.setObjectName("Card")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        add_shadow(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel(action.name or "(Unnamed)")
        subtitle = QLabel(action.action_type.name.replace("_", " ").title())
        subtitle.setProperty("class", "subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        top.addLayout(title_box)
        top.addStretch(1)
        notation_label = QLabel(self._notation_for(action))
        top.addWidget(notation_label)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self._remove_action(card, action))
        top.addWidget(remove_btn)
        layout.addLayout(top)

        if action.desc:
            body = QLabel(action.desc)
            body.setWordWrap(True)
            layout.addWidget(body)

        self._cards_layout.addWidget(card)

    def _add_action(self) -> None:
        action_type = self.type_combo.currentData()
        roll = Rollable(num=self.num_input.value(), sides=self.sides_input.value())
        mod_val = self.mod_input.value()
        if mod_val:
            roll.modifier = Modifier(target="roll", op=Op.ADD, value=mod_val)
        name = self.name_input.text().strip() or None
        desc = self.desc_input.text().strip() or None
        action = Action(action_type=action_type, roll=roll, name=name, desc=desc)
        self._actions.append(action)
        self._render_card(action)
        # reset inputs
        self.name_input.clear()
        self.desc_input.clear()
        self.num_input.setValue(1)
        self.sides_input.setValue(6)
        self.mod_input.setValue(0)

    def _remove_action(self, card: QFrame, action: Action) -> None:
        self._actions.remove(action)
        card.setParent(None)
        card.deleteLater()

    def get_actions(self) -> list[Action]:
        return list(self._actions)
