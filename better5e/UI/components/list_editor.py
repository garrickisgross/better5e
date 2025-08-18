from __future__ import annotations

from typing import Generic, List, TypeVar

from PyQt6.QtWidgets import QWidget

T = TypeVar("T")


class ListEditor(QWidget, Generic[T]):
    """Simple list editor storing a list of items.

    This widget is intentionally lightweight and focuses on data handling so
    that it can be exercised in unit tests without showing UI.  It exposes a
    small API for adding, duplicating, deleting and reordering items while
    keeping the :pyattr:`items` list in sync.
    """

    def __init__(self, item_type: type[T], items: list[T] | None = None) -> None:
        super().__init__()
        self.item_type = item_type
        self.items: List[T] = list(items) if items else []

    # ------------------------------------------------------------------
    def add(self, item: T) -> None:
        """Append *item* to the editor."""

        self.items.append(item)

    # ------------------------------------------------------------------
    def duplicate(self, index: int) -> None:
        """Duplicate the item at *index* and insert it directly after."""

        self.items.insert(index + 1, self.items[index])

    # ------------------------------------------------------------------
    def delete(self, index: int) -> None:
        """Remove the item at *index* from the editor."""

        del self.items[index]

    # ------------------------------------------------------------------
    def move(self, src: int, dest: int) -> None:
        """Move an item from *src* to *dest* preserving order."""

        item = self.items.pop(src)
        self.items.insert(dest, item)
