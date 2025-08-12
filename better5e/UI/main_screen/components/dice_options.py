from __future__ import annotations

from typing import Dict, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QToolButton,
    QLineEdit,
    QSizePolicy,
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

        minus = QToolButton(text="–")
        minus.setObjectName("ModBtn")
        minus.setFixedSize(40, 40)

        plus = QToolButton(text="+")
        plus.setObjectName("ModBtn")
        plus.setFixedSize(40, 40)

        edit = QLineEdit("0")
        edit.setObjectName("ModEdit")
        edit.setValidator(QIntValidator(-999, 999, self))
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        edit.setFixedWidth(72)
        edit.setMinimumHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(minus)
        layout.addWidget(edit)
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

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(12)

        # --- Dice grid ---------------------------------------------------
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        self.die_buttons: dict[int, DieButton] = {}

        for i, sides in enumerate(DICE_SIDES):
            row, col = divmod(i, 4)
            btn = DieButton(sides)
            btn.setObjectName("DieBtn")
            btn.setMinimumSize(88, 44)
            btn.setMaximumHeight(44)
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            btn.countChanged.connect(self._update_roll_enabled)
            grid.addWidget(btn, row, col)
            self.die_buttons[sides] = btn

        for c in range(4):
            grid.setColumnStretch(c, 1)

        root.addLayout(grid)

        # --- Modifier row (compact, centered) ---------------------------
        modWrap = QHBoxLayout()
        modWrap.setContentsMargins(0, 0, 0, 0)
        modWrap.setSpacing(10)
        modWrap.addStretch(1)

        self.modifierControl = ModifierControl()
        modWrap.addWidget(self.modifierControl)
        modWrap.addStretch(1)

        root.addLayout(modWrap)

        # --- Actions (full width) --------------------------------------
        self.resetBtn = QPushButton("Reset")
        self.resetBtn.setObjectName("ResetBtn")
        self.rollBtn = QPushButton("Roll")
        self.rollBtn.setObjectName("RollBtn")

        for b in (self.resetBtn, self.rollBtn):
            b.setMinimumHeight(46)
            b.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            root.addWidget(b)

        # signals -------------------------------------------------------
        self.resetBtn.clicked.connect(self.reset)
        self.rollBtn.clicked.connect(self.roll)
        QShortcut(QKeySequence("R"), self, activated=self.roll)
        QShortcut(QKeySequence("Esc"), self, activated=self.reset)

        self.rollBtn.setEnabled(False)

        # backward-compatible attribute names
        self.roll_btn = self.rollBtn
        self.reset_btn = self.resetBtn
        self.mod_ctrl = self.modifierControl

    # utilities ---------------------------------------------------------
    def _update_roll_enabled(self, *_: int) -> None:
        total = sum(btn.count for btn in self.die_buttons.values())
        self.rollBtn.setEnabled(total > 0)

    def reset(self) -> None:
        for btn in self.die_buttons.values():
            btn.count = 0
        self.modifierControl.setValue(0)
        self._update_roll_enabled()
        self.resetRequested.emit()

    def roll(self) -> None:
        dice = {s: b.count for s, b in self.die_buttons.items() if b.count}
        if not dice:
            return
        self.rollRequested.emit(dice, self.modifierControl.value)

    def state(self) -> Tuple[Dict[int, int], int]:
        dice = {s: b.count for s, b in self.die_buttons.items() if b.count}
        return dice, self.modifierControl.value

    def get_notation(self) -> str:
        dice, mod = self.state()
        parts = [f"{cnt}d{s}" for s, cnt in dice.items()]
        notation = " + ".join(parts)
        if mod:
            sign = "+" if mod > 0 else "-"
            notation = f"{notation} {sign} {abs(mod)}" if notation else f"{mod}"
        return notation.strip()

