from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
)

from pydantic import BaseModel

from better5e.UI.homebrew.dnd import DropZone
from better5e.models.enums import ActionType


LABEL_OVERRIDES = {
    "desc": "Description",
    "uses_max": "Maximum Uses",
    "recharge": "Recharge Type",
    "grants": "Grants",
    "actions": "Actions",
    "modifiers": "Modifiers",
}


class ActionRow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        self.type = QComboBox()
        self.type.addItem("", "")
        for val in ActionType:
            self.type.addItem(val.value.replace("_", " ").title(), val.value)
        self.num = QSpinBox()
        self.num.setMinimum(1)
        self.num.setMaximum(1_000)
        self.sides = QSpinBox()
        self.sides.setMinimum(1)
        self.sides.setMaximum(1_000)
        remove = QToolButton()
        remove.setText("✕")
        remove.clicked.connect(self._remove)
        layout.addWidget(self.type)
        layout.addWidget(self.num)
        layout.addWidget(self.sides)
        layout.addWidget(remove)

    def _remove(self) -> None:
        self.setParent(None)
        self.deleteLater()

    def payload(self) -> dict[str, Any] | None:
        action_type = self.type.currentData()
        if not action_type:
            return None
        roll = {"num": self.num.value(), "sides": self.sides.value()}
        return {"action_type": action_type, "roll": roll}


class ActionsEditor(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.rows = QVBoxLayout()
        layout.addLayout(self.rows)
        add = QPushButton("Add Action")
        add.clicked.connect(self._add_row)
        layout.addWidget(add)
        self._add_row()

    def _add_row(self) -> None:
        row = ActionRow()
        self.rows.addWidget(row)

    def actions(self) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        for i in range(self.rows.count()):
            row = self.rows.itemAt(i).widget()
            if row is None:
                continue
            payload = row.payload()
            if payload:
                actions.append(payload)
        return actions


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
        self.labels: dict[str, str] = {}
        self._build()

    # building --------------------------------------------------------
    def _build(self) -> None:
        for name, info in self.schema["properties"].items():
            if name in {"id", "kind"}:
                continue
            self.widgets[name] = self._widget_for_field(name, info)
            title = info.get("title") or name.replace("_", " ").title()
            self.labels[name] = LABEL_OVERRIDES.get(name, title)

    def _widget_for_field(self, name: str, info: dict[str, Any]) -> QWidget:
        if "anyOf" in info or "oneOf" in info:
            opts = info.get("anyOf") or info.get("oneOf")
            for opt in opts:
                t = opt.get("type")
                if t and t != "null":
                    info = opt
                    break
                if "$ref" in opt:
                    info = opt
                    break
        if "$ref" in info:
            ref = info["$ref"].split("/")[-1]
            info = self.schema.get("$defs", {}).get(ref, {})
        if info.get("enum"):
            w = QComboBox()
            w.addItem("", "")
            for val in info["enum"]:
                w.addItem(val.replace("_", " ").title(), val)
            return w
        t = info.get("type")
        if t == "string":
            return QPlainTextEdit() if name == "desc" else QLineEdit()
        if t == "integer":
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
        if name == "actions":
            return ActionsEditor()
        return QLabel("(Coming soon)")

    # API -------------------------------------------------------------
    def widgets_for(self, field: str) -> QWidget:
        return self.widgets[field]

    def label_for(self, field: str) -> str:
        return self.labels[field]

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
            elif isinstance(w, QComboBox):
                current = w.currentData()
                val = current or None
            elif isinstance(w, DropZone):
                val = w.uuids()
            elif isinstance(w, ActionsEditor):
                val = w.actions()
            else:  # QLabel placeholder
                val = None
            if name in self.required and (val is None or val == "" or val == []):
                errors[name] = "required"
            elif val is not None and val != "":
                data[name] = val
        if errors:
            raise ValidationErrorUI(errors)
        return data
