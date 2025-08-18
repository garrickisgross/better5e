from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QFrame,
    QHBoxLayout,
)

from better5e.models.game_object import Modifier, Op


class _ModifierRow(QFrame):
    def __init__(self, remove_cb) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        self.target_edit = QLineEdit()
        layout.addWidget(self.target_edit)
        self.op_combo = QComboBox()
        for op in Op:
            self.op_combo.addItem(op.name.title(), op)
        layout.addWidget(self.op_combo)
        self.value_spin = QSpinBox()
        self.value_spin.setMinimum(-9999)
        self.value_spin.setMaximum(9999)
        layout.addWidget(self.value_spin)
        rm = QPushButton("Remove")
        rm.clicked.connect(lambda: remove_cb(self))
        layout.addWidget(rm)

    def to_model(self) -> Modifier:
        return Modifier(
            target=self.target_edit.text(),
            op=self.op_combo.currentData(),
            value=self.value_spin.value(),
        )


class ModifiersEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.rows_layout = QVBoxLayout()
        layout.addLayout(self.rows_layout)
        add_btn = QPushButton("Add Modifier")
        add_btn.clicked.connect(self.add_row)
        layout.addWidget(add_btn)
        self._rows: list[_ModifierRow] = []

    def add_row(self) -> None:
        row = _ModifierRow(self.remove_row)
        self._rows.append(row)
        self.rows_layout.addWidget(row)

    def remove_row(self, row: _ModifierRow) -> None:
        self._rows.remove(row)
        self.rows_layout.removeWidget(row)
        row.deleteLater()

    def modifiers(self) -> list[Modifier]:
        return [r.to_model() for r in self._rows]
