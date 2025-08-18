from __future__ import annotations

from typing import List

from PyQt6.QtWidgets import QWidget


class GrantPicker(QWidget):
    """Placeholder widget representing a grant picker.

    The real application would provide drag-and-drop and database lookups. For
    unit testing we only need to maintain a list of selected grant UUIDs.
    """

    def __init__(self, grants: List[str] | None = None) -> None:
        super().__init__()
        self.grants: List[str] = list(grants) if grants else []

    def add_grant(self, grant_id: str) -> None:
        self.grants.append(grant_id)

    def remove_grant(self, grant_id: str) -> None:
        self.grants.remove(grant_id)
