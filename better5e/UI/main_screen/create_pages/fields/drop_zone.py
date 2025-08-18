from uuid import UUID
from PyQt6.QtWidgets import QWidget


class DropZone(QWidget):
    """Simplified drop zone collecting UUIDs."""

    def __init__(self):
        super().__init__()
        self._uuids: list[UUID] = []

    def add_uuid(self, value: UUID) -> None:
        self._uuids.append(value)

    def remove_uuid(self, value: UUID) -> None:
        if value in self._uuids:
            self._uuids.remove(value)

    def values(self) -> list[UUID]:
        return list(self._uuids)
