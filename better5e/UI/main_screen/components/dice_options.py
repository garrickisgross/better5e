import random

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QWidget,
    QComboBox,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
)


class DiceOptionsPanel(QWidget):
    """Controls for choosing dice, count and modifier."""

    rollMade = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)

        self.die_box = QComboBox()
        self.die_box.addItems(["d4", "d6", "d8", "d10", "d12", "d20", "d100"])
        layout.addWidget(self.die_box)

        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 10)
        layout.addWidget(self.count_spin)

        self.mod_spin = QSpinBox()
        self.mod_spin.setRange(-20, 20)
        layout.addWidget(self.mod_spin)

        self.roll_btn = QPushButton("Roll")
        self.roll_btn.setProperty("class", "primary")
        layout.addWidget(self.roll_btn)

        self.roll_btn.clicked.connect(self.roll)

        shortcut = QShortcut(QKeySequence("R"), self)
        shortcut.activated.connect(self.roll)
        self._shortcut = shortcut  # keep reference

    def roll(self) -> None:
        """Roll dice according to current settings and emit result string."""
        sides = int(self.die_box.currentText()[1:])
        count = self.count_spin.value()
        mod = self.mod_spin.value()
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results) + mod
        msg = (
            f"{count}d{sides}{mod:+d} = {total} (" + ", ".join(map(str, results)) + ")"
        )
        self.rollMade.emit(msg)
