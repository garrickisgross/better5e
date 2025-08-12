from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QPushButton, QGridLayout


class DieButton(QPushButton):
    """Button representing a single die type with a count badge."""

    countChanged = pyqtSignal(int)

    def __init__(self, sides: int) -> None:
        super().__init__(f"d{sides}")
        self.setObjectName("DieButton")
        self.setProperty("class", "die")
        self.sides = sides
        self._count = 0

        badge = QLabel("0", self)
        badge.setObjectName("DieBadge")
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(badge, 0, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        badge.hide()
        self.badge = badge

    # count property -----------------------------------------------------
    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        value = max(0, min(99, value))
        if self._count == value:
            return
        self._count = value
        self.badge.setText("9+" if value > 9 else str(value))
        self.badge.setVisible(value > 0)
        self.countChanged.emit(value)

    # events -------------------------------------------------------------
    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.count += 1
            event.accept()
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.count -= 1
            event.accept()
            return
        super().mousePressEvent(event)

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        delta = event.angleDelta().y()
        if delta > 0:
            self.count += 1
        elif delta < 0:
            self.count -= 1
        event.accept()
