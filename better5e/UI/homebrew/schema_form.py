from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from PyQt6.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QWidget,
    QLabel,
)

from pydantic import BaseModel

from better5e.UI.homebrew.dnd import DropZone


class ValidationErrorUI(Exception):
    """Raised when form values fail basic validation."""

    def __init__(self, errors: dict[str, str]):
        super().__init__("validation error")
        self.errors = errors


class SchemaFormBuilder:
    """Build widgets for a Pydantic model schema."""

    def __init__(self, model: type[BaseModel] | BaseModel):
        self.model = model if isinstance(model, type) else type(model)
        self.instance = None if isinstance(model, type) else model
        self.schema = self.model.model_json_schema()
        self.required = set(self.schema.get("required", []))
        self.widgets: dict[str, QWidget] = {}
        self._build()

    # building --------------------------------------------------------
    def _build(self) -> None:
        for name, info in self.schema["properties"].items():
            if name in {"id", "kind"}:
                continue
            self.widgets[name] = self._widget_for_field(name, info)

    def _widget_for_field(self, name: str, info: dict[str, Any]) -> QWidget:
        if info.get("enum"):  # pragma: no cover - unused in tests
            w = QComboBox()
            w.addItem("")
            for val in info["enum"]:
                w.addItem(val)
            return w
        t = info.get("type")
        if t == "string":
            return QPlainTextEdit() if name == "desc" else QLineEdit()
        if t == "integer":  # pragma: no cover - unused in tests
            sb = QSpinBox()
            sb.setMaximum(1_000_000_000)
            return sb
        if t == "number":  # pragma: no cover - unused in tests
            sb = QDoubleSpinBox()
            sb.setMaximum(1_000_000_000)
            return sb
        if t == "boolean":  # pragma: no cover - unused in tests
            return QCheckBox()
        if t == "array" and info.get("items", {}).get("format") == "uuid":
            return DropZone()
        return QLabel("(Coming soon)")

    # API -------------------------------------------------------------
    def widgets_for(self, field: str) -> QWidget:
        return self.widgets[field]

    def set_errors(self, errors: dict[str, str]) -> None:
        for name, msg in errors.items():
            w = self.widgets.get(name)
            if w is not None:
                w.setProperty("error", True)
                w.setToolTip(msg)

    def get_payload(self) -> dict[str, Any]:
        data = {}
        errors: dict[str, str] = {}
        for name, w in self.widgets.items():
            val: Any
            if isinstance(w, QLineEdit):
                val = w.text()
            elif isinstance(w, QPlainTextEdit):  # pragma: no cover - unused
                val = w.toPlainText()
            elif isinstance(w, QSpinBox):  # pragma: no cover - unused
                val = w.value()
            elif isinstance(w, QDoubleSpinBox):  # pragma: no cover - unused
                val = w.value()
            elif isinstance(w, QCheckBox):  # pragma: no cover - unused
                val = w.isChecked()
            elif isinstance(w, QComboBox):  # pragma: no cover - unused
                text = w.currentText()
                val = text or None
            elif isinstance(w, DropZone):
                val = w.uuids()
            else:  # QLabel placeholder
                val = None
            if name in self.required and (val is None or val == "" or val == []):
                errors[name] = "required"
            elif val is not None and val != "":
                data[name] = val
        if errors:
            raise ValidationErrorUI(errors)
        return data
