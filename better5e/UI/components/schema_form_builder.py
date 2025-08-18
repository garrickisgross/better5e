from __future__ import annotations

from typing import Any, Iterable

from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QComboBox,
)


class SchemaFormBuilder:
    """Very small helper that builds form fields from a schema."""

    def __init__(self) -> None:
        self.fields: dict[str, QWidget] = {}
        self.widget: QWidget | None = None

    @staticmethod
    def label_for(name: str) -> str:
        return name.replace("_", " ").title()

    def build(self, schema: dict[str, tuple[type[QWidget], dict[str, Any] | None]]) -> QWidget:
        self.widget = QWidget()
        layout = QFormLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for field, (cls, opts) in schema.items():
            widget = cls()
            opts = opts or {}
            if isinstance(widget, QSpinBox):
                widget.setMinimum(opts.get("min", 0))
            if isinstance(widget, QComboBox):
                enum: Iterable[Any] | None = opts.get("enum")
                widget.addItem("", None)
                if enum:
                    for item in enum:
                        label = getattr(item, "name", str(item)).replace("_", " ").title()
                        widget.addItem(label, item)
            layout.addRow(self.label_for(field), widget)
            self.fields[field] = widget
        return self.widget
