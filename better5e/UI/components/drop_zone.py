from __future__ import annotations

import json
from uuid import UUID

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout


class DropZone(QWidget):
    """Simple widget that accepts drops and shows removable chips."""

    changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.ids: list[UUID] = []

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:  # pragma: no cover - Qt
        if e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent) -> None:  # pragma: no cover - Qt
        try:
            payload = json.loads(e.mimeData().text())
            uid = UUID(payload["id"])
            name = payload.get("name", str(uid))
            self.add_uuid(uid, name)
            e.acceptProposedAction()
        except Exception:
            pass

    def add_uuid(self, uid: UUID, name: str) -> None:
        if uid in self.ids:
            return
        chip = QPushButton(name)
        chip.setProperty("class", "chip")
        chip.clicked.connect(lambda: self._remove_chip(chip, uid))
        self.layout.addWidget(chip)
        self.ids.append(uid)
        self.changed.emit()

    def _remove_chip(self, chip: QPushButton, uid: UUID) -> None:
        self.layout.removeWidget(chip)
        chip.deleteLater()
        if uid in self.ids:
            self.ids.remove(uid)
        self.changed.emit()
