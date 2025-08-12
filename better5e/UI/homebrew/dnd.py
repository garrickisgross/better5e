from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable, Optional
from uuid import UUID

from PyQt6.QtCore import QMimeData, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QWidget,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QFrame,
    QVBoxLayout,
)


@dataclass
class Record:
    """Simple data object used for drag-and-drop."""

    uuid: UUID
    kind: str
    name: str


def mime_from_record(record: Record) -> QMimeData:
    """Create a QMimeData payload for a record."""

    mime = QMimeData()
    payload = json.dumps({"uuid": str(record.uuid), "kind": record.kind, "name": record.name})
    mime.setData("application/better5e-record", payload.encode("utf-8"))
    return mime


def parse_mime(event) -> Optional[Record]:
    """Extract a Record from a drag/drop event."""

    md = event.mimeData()
    if md.hasFormat("application/better5e-record"):
        data = json.loads(bytes(md.data("application/better5e-record")))
        data["uuid"] = UUID(data["uuid"])
        return Record(**data)
    return None


class CatalogList(QListWidget):
    """List widget that provides draggable records."""

    def __init__(self) -> None:
        super().__init__()
        self.setDragEnabled(True)

    def add_record(self, record: Record) -> None:
        item = QListWidgetItem(record.name)
        item.setData(Qt.ItemDataRole.UserRole, record)
        self.addItem(item)

    def mimeData(self, items: Iterable[QListWidgetItem]) -> QMimeData:  # pragma: no cover - Qt calls
        if not items:
            return QMimeData()
        record = items[0].data(Qt.ItemDataRole.UserRole)
        return mime_from_record(record)


class Chip(QWidget):
    """Small widget representing an attached record."""

    removed = pyqtSignal(UUID)

    def __init__(self, record: Record):
        super().__init__()
        self.record = record
        lay = QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lab = QLabel(f"{record.name} ({record.kind})")
        btn = QToolButton()
        btn.setText("x")
        btn.clicked.connect(lambda: self.removed.emit(record.uuid))
        lay.addWidget(lab)
        lay.addWidget(btn)


class DropZone(QFrame):
    """Accepts drops of Records and renders them as chips."""

    def __init__(self, accept_kinds: Optional[list[str]] = None, multi: bool = True):
        super().__init__()
        self.accept_kinds = accept_kinds
        self.multi = multi
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self._records: list[Record] = []
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(4)

    # dnd -------------------------------------------------------------
    def dragEnterEvent(self, event):  # pragma: no cover - tested via helper
        rec = parse_mime(event)
        if rec and self._can_accept(rec):
            event.acceptProposedAction()

    def dropEvent(self, event):  # pragma: no cover - tested via helper
        rec = parse_mime(event)
        if rec:
            self.add_record(rec)
            event.acceptProposedAction()

    # helpers ---------------------------------------------------------
    def _can_accept(self, rec: Record) -> bool:
        if self.accept_kinds and rec.kind not in self.accept_kinds:
            return False
        if not self.multi and self._records:
            return False
        if any(r.uuid == rec.uuid for r in self._records):
            return False
        return True

    def add_record(self, rec: Record) -> None:
        if not self._can_accept(rec):
            return
        chip = Chip(rec)
        chip.removed.connect(self._remove)
        self._records.append(rec)
        self._layout.addWidget(chip)

    def _remove(self, uid: UUID) -> None:
        self._records = [r for r in self._records if r.uuid != uid]
        chip = self.sender()
        if isinstance(chip, QWidget):
            chip.setParent(None)
            chip.deleteLater()

    # public API ------------------------------------------------------
    def uuids(self) -> list[UUID]:
        return [r.uuid for r in self._records]
