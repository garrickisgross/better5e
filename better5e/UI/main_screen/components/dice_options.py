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
    QLabel,
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

    rollRequested = pyqtSignal(dict, int, dict)
    resetRequested = pyqtSignal()

    def __init__(self, *, compact: bool = True, parent: QWidget | None = None) -> None:
        """Create the dice options panel.

        Parameters
        ----------
        compact:
            Whether to use tighter vertical spacing for controls.
        parent:
            Optional parent widget.
        """
        super().__init__(parent)

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
            btn.countChanged.connect(self._on_die_changed)
            row, col = divmod(i, 4)
            grid.addWidget(btn, row, col)
            self.die_buttons[sides] = btn

        self._build_selected_row()
        root.addWidget(self.selectedWidget)

        self.modifierControl = ModifierControl()
        root.addWidget(self.modifierControl)

        flags_row = QHBoxLayout()
        flags_row.setContentsMargins(0, 0, 0, 0)
        flags_row.setSpacing(6)
        adv_btn = QToolButton()
        adv_btn.setText("Adv")
        adv_btn.setCheckable(True)
        dis_btn = QToolButton()
        dis_btn.setText("Dis")
        dis_btn.setCheckable(True)
        adv_btn.toggled.connect(lambda v: dis_btn.setChecked(False) if v else None)
        dis_btn.toggled.connect(lambda v: adv_btn.setChecked(False) if v else None)
        flags_row.addWidget(adv_btn)
        flags_row.addWidget(dis_btn)
        flags_row.addStretch(1)
        root.addLayout(flags_row)

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

        root.addWidget(reset_btn)
        root.addWidget(roll_btn)

        reset_btn.clicked.connect(self.reset)
        roll_btn.clicked.connect(self.roll)

        QShortcut(QKeySequence("R"), self, activated=self.roll)
        QShortcut(QKeySequence("Esc"), self, activated=self.reset)
        QShortcut(QKeySequence("Ctrl+Backspace"), self, activated=self.reset)
        for idx, sides in enumerate(DICE_SIDES, start=1):
            QShortcut(QKeySequence(str(idx)), self, activated=lambda s=sides: setattr(self.die_buttons[s], "count", self.die_buttons[s].count + 1))

        self.rollBtn = roll_btn
        self.resetBtn = reset_btn
        # backward-compatible attribute names
        self.roll_btn = self.rollBtn
        self.reset_btn = self.resetBtn
        self.mod_ctrl = self.modifierControl
        self.advBtn = adv_btn
        self.disBtn = dis_btn

        # tighten vertical rhythm
        root.setSpacing(8)
        root.setContentsMargins(8, 6, 8, 8)

        dense_h_btn = 38 if compact else 44
        dense_h_edit = 38 if compact else 44

        for btn in self.findChildren(
            QPushButton, options=Qt.FindChildOption.FindChildrenRecursively
        ):
            if btn.property("class") == "die":
                btn.setMinimumHeight(dense_h_btn)
        self.resetBtn.setMinimumHeight(dense_h_btn)
        self.rollBtn.setMinimumHeight(dense_h_btn + 6)

        # modifier controls
        self.modifierControl.edit.setMinimumHeight(dense_h_edit)
        self.modifierControl.minus.setMinimumHeight(dense_h_edit)
        self.modifierControl.plus.setMinimumHeight(dense_h_edit)

    # utilities ----------------------------------------------------------
    def _update_roll_enabled(self, *_: int) -> None:
        total = sum(btn.count for btn in self.die_buttons.values())
        self.rollBtn.setEnabled(total > 0)

    def _on_die_changed(self, *_: int) -> None:
        self._update_roll_enabled()
        self._refresh_selected_row()

    def reset(self) -> None:
        for btn in self.die_buttons.values():
            btn.count = 0
        self.modifierControl.setValue(0)
        self._update_roll_enabled()
        self._refresh_selected_row()
        self.advBtn.setChecked(False)
        self.disBtn.setChecked(False)
        self.resetRequested.emit()

    def roll(self) -> None:
        dice = {sides: btn.count for sides, btn in self.die_buttons.items() if btn.count}
        if not dice:
            return
        flags = {"adv": self.advBtn.isChecked(), "dis": self.disBtn.isChecked()}
        self.rollRequested.emit(dice, self.modifierControl.value, flags)

    def state(self) -> Tuple[Dict[int, int], int]:
        dice = {sides: btn.count for sides, btn in self.die_buttons.items() if btn.count}
        return dice, self.modifierControl.value

    def get_notation(self) -> str:
        dice, mod = self.state()
        parts = [f"{cnt}d{sides}" for sides, cnt in dice.items()]
        notation = " + ".join(parts)
        if mod:
            sign = "+" if mod > 0 else "-"
            notation = f"{notation} {sign} {abs(mod)}" if notation else f"{mod}"
        return notation.strip()

    # selected row ------------------------------------------------------
    def _build_selected_row(self) -> None:
        self.selectedWidget = QWidget()
        row = QHBoxLayout(self.selectedWidget)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        self.selectedRow = row
        self._refresh_selected_row()

    def _refresh_selected_row(self) -> None:
        row = self.selectedRow
        while row.count():
            item = row.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for sides, btn in self.die_buttons.items():
            if btn.count:
                lab = QLabel(f"d{sides}\xd7{btn.count} \xd7")
                lab.setProperty("class", "chip")
                lab.mousePressEvent = lambda _e, s=sides: setattr(self.die_buttons[s], "count", self.die_buttons[s].count - 1)
                row.addWidget(lab)
        row.addStretch(1)
