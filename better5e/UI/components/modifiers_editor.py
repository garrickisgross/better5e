from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
)

from better5e.UI.core.style.tokens import gutter
from better5e.UI.core.style.theme import add_shadow
from better5e.UI.components.section_header import SectionHeader
from better5e.models.game_object import Modifier
from better5e.models.enums import Op


class ModifiersEditor(QWidget):
    """Widget for editing a list of :class:`Modifier` objects."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(gutter(), gutter(), gutter(), gutter())
        layout.setSpacing(12)

        self._list_layout = QVBoxLayout()
        self._list_layout.setSpacing(12)
        layout.addLayout(self._list_layout)

        header = SectionHeader("Add Modifier")
        header.button.hide()
        layout.addWidget(header)

        form = QHBoxLayout()
        form.setSpacing(12)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("target")
        form.addWidget(self.target_input)

        self.op_input = QComboBox()
        for op in Op:
            self.op_input.addItem(op.name.title(), op)
        form.addWidget(self.op_input)

        self.value_input = QSpinBox()
        self.value_input.setRange(-999, 999)
        form.addWidget(self.value_input)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_modifier)
        form.addWidget(add_btn)

        layout.addLayout(form)
        layout.addStretch(1)

        self._modifiers: list[Modifier] = []

    # ------------------------------------------------------------------
    def _render_modifier(self, mod: Modifier) -> None:
        card = QFrame()
        card.setObjectName("Card")
        card.setFrameShape(QFrame.Shape.StyledPanel)
        add_shadow(card)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        layout.addWidget(QLabel(mod.target))
        layout.addWidget(QLabel(mod.op.name))
        layout.addWidget(QLabel(str(mod.value) if mod.value is not None else ""))
        layout.addStretch(1)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self._remove_modifier(card, mod))
        layout.addWidget(remove_btn)

        self._list_layout.addWidget(card)

    def _add_modifier(self) -> None:
        target = self.target_input.text().strip()
        if not target:
            return
        op = self.op_input.currentData()
        value = self.value_input.value()
        mod = Modifier(target=target, op=op, value=value)
        self._modifiers.append(mod)
        self._render_modifier(mod)
        self.target_input.clear()
        self.value_input.setValue(0)

    def _remove_modifier(self, card: QFrame, mod: Modifier) -> None:
        self._modifiers.remove(mod)
        card.setParent(None)
        card.deleteLater()

    def get_modifiers(self) -> list[Modifier]:
        return list(self._modifiers)
