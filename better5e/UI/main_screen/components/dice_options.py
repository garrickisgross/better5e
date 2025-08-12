from __future__ import annotations

from typing import Dict, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QToolButton,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
)

from better5e.UI.main_screen.components.die_button import DieButton


DICE_SIDES = [2, 4, 6, 8, 10, 12, 20, 100]


class ModifierControl(QWidget):
    """Numeric modifier widget with +/− buttons."""

    valueChanged = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("ModifierControl")
        self._val = 0

        minus = QToolButton()
        minus.setText("-")
        plus = QToolButton()
        plus.setText("+")
        edit = QLineEdit("0")
        edit.setValidator(QIntValidator(-999, 999, self))
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(minus)
        layout.addWidget(edit, 1)
        layout.addWidget(plus)

        minus.clicked.connect(lambda: self.setValue(self._val - 1))
        plus.clicked.connect(lambda: self.setValue(self._val + 1))
        edit.textChanged.connect(self._on_text_changed)

        self.minus = minus
        self.plus = plus
        self.edit = edit

    def _on_text_changed(self, text: str) -> None:
        try:
            val = int(text)
        except ValueError:
            val = 0
        self._val = max(-999, min(999, val))
        if self.edit.text() != str(self._val):
            self.edit.setText(str(self._val))
        self.valueChanged.emit(self._val)

    def setValue(self, value: int) -> None:
        value = max(-999, min(999, value))
        if value == self._val:
            return
        self._val = value
        self.edit.setText(str(value))
        self.valueChanged.emit(value)

    @property
    def value(self) -> int:
        return self._val


class DiceOptionsPanel(QWidget):
    """Modern dice pad allowing multiple dice selection."""

    rollRequested = pyqtSignal(dict, int)
    resetRequested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(12)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        root.addLayout(grid)

        self.die_buttons: dict[int, DieButton] = {}
        for i, sides in enumerate(DICE_SIDES):
            btn = DieButton(sides)
            btn.setToolTip("Coin flip (d2)" if sides == 2 else f"d{sides}")
            btn.countChanged.connect(self._update_roll_enabled)
            row, col = divmod(i, 4)
            grid.addWidget(btn, row, col)
            self.die_buttons[sides] = btn

        self.mod_ctrl = ModifierControl()
        root.addWidget(self.mod_ctrl)

        root.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("ResetBtn")
        reset_btn.setProperty("class", "secondary")
        roll_btn = QPushButton("Roll")
        roll_btn.setObjectName("RollBtn")
        roll_btn.setProperty("class", "primary")
        roll_btn.setEnabled(False)

        for b in (reset_btn, roll_btn):
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setMinimumHeight(44)

        root.addWidget(reset_btn)
        root.addWidget(roll_btn)

        reset_btn.clicked.connect(self.reset)
        roll_btn.clicked.connect(self.roll)

        QShortcut(QKeySequence("R"), self, activated=self.roll)
        QShortcut(QKeySequence("Esc"), self, activated=self.reset)

        self.roll_btn = roll_btn
        self.reset_btn = reset_btn

    # utilities ----------------------------------------------------------
    def _update_roll_enabled(self, *_: int) -> None:
        total = sum(btn.count for btn in self.die_buttons.values())
        self.roll_btn.setEnabled(total > 0)

    def reset(self) -> None:
        for btn in self.die_buttons.values():
            btn.count = 0
        self.mod_ctrl.setValue(0)
        self._update_roll_enabled()
        self.resetRequested.emit()

    def roll(self) -> None:
        dice = {sides: btn.count for sides, btn in self.die_buttons.items() if btn.count}
        if not dice:
            return
        self.rollRequested.emit(dice, self.mod_ctrl.value)

    def state(self) -> Tuple[Dict[int, int], int]:
        dice = {sides: btn.count for sides, btn in self.die_buttons.items() if btn.count}
        return dice, self.mod_ctrl.value

    def get_notation(self) -> str:
        dice, mod = self.state()
        parts = [f"{cnt}d{sides}" for sides, cnt in dice.items()]
        notation = " + ".join(parts)
        if mod:
            sign = "+" if mod > 0 else "-"
            notation = f"{notation} {sign} {abs(mod)}" if notation else f"{mod}"
        return notation.strip()
