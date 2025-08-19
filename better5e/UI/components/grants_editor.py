from __future__ import annotations

from uuid import UUID

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QInputDialog,
    QMessageBox,
)

from better5e.UI.core.style.tokens import gutter
from better5e.UI.components.section_header import SectionHeader


class GrantsEditor(QWidget):
    """Widget for editing a list of granted UUIDs."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(gutter(), gutter(), gutter(), gutter())
        layout.setSpacing(12)

        header = SectionHeader("Grants")
        header.button.hide()
        layout.addWidget(header)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btns = QHBoxLayout()
        add_btn = QPushButton("Add UUID")
        add_btn.clicked.connect(self._add_uuid)
        btns.addWidget(add_btn)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_selected)
        btns.addWidget(remove_btn)
        btns.addStretch(1)
        layout.addLayout(btns)
        layout.addStretch(1)

    # ------------------------------------------------------------------
    def _add_uuid(self) -> None:
        text, ok = QInputDialog.getText(self, "Add UUID", "UUID:")
        if not ok or not text:
            return
        try:
            uid = UUID(text)
        except ValueError:
            QMessageBox.warning(self, "Invalid UUID", "Please enter a valid UUID.")
            return
        self.list_widget.addItem(str(uid))

    def _remove_selected(self) -> None:
        for item in self.list_widget.selectedItems():
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

    def get_grants(self) -> list[UUID]:
        return [UUID(self.list_widget.item(i).text()) for i in range(self.list_widget.count())]
