from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QComboBox,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QFormLayout,
)

from pydantic import BaseModel

from better5e.UI.homebrew.dnd import DropZone
from better5e.UI.style.theme import add_shadow
from better5e.models.enums import ActionType


LABEL_OVERRIDES = {
    "desc": "Description",
    "uses_max": "Maximum Uses",
    "recharge": "Recharge Type",
    "grants": "Grants",
    "actions": "Actions",
    "modifiers": "Modifiers",
}


class ActionCard(QFrame):
    def __init__(self, data: dict[str, Any], remove: Callable[["ActionCard"], None]):
        super().__init__()
        self.setObjectName("Card")
        add_shadow(self)
        self.data = data

        layout = QHBoxLayout(self)
        info = QVBoxLayout()

        title_txt = data.get("name") or data["action_type"].replace("_", " ").title()
        title = QLabel(title_txt)
        title.setObjectName("CardTitle")
        info.addWidget(title)

        subtitle = QLabel(data["action_type"].replace("_", " ").title())
        subtitle.setObjectName("CardSubtitle")
        info.addWidget(subtitle)

        if data.get("desc"):
            body = QLabel(data["desc"])
            body.setObjectName("CardBody")
            body.setWordWrap(True)
            info.addWidget(body)

        layout.addLayout(info)
        layout.addStretch(1)

        roll = data.get("roll")
        if roll:
            roll_lbl = QLabel(f"{roll['num']}d{roll['sides']}")
            roll_lbl.setObjectName("CardRoll")
            layout.addWidget(roll_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        btn = QToolButton()
        btn.setText("✕")
        btn.clicked.connect(lambda: remove(self))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignTop)


class ActionsEditor(QWidget):
    def __init__(self, labels: dict[str, str]):
        super().__init__()
        self._labels = labels
        self._data: list[dict[str, Any]] = []
        layout = QVBoxLayout(self)
        self.cards = QVBoxLayout()
        layout.addLayout(self.cards)
        form = QFormLayout()
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
        self.name = QLineEdit()
        self.desc = QLineEdit()
        form.addRow(labels["type"], self.type)
        form.addRow(labels["num"], self.num)
        form.addRow(labels["sides"], self.sides)
        form.addRow(labels["name"], self.name)
        form.addRow(labels["desc"], self.desc)
        layout.addLayout(form)
        add = QPushButton("Add Action")
        add.clicked.connect(self._add_action)
        layout.addWidget(add)

    def _clear_form(self) -> None:
        self.type.setCurrentIndex(0)
        self.num.setValue(1)
        self.sides.setValue(20)
        self.name.clear()
        self.desc.clear()

    def _add_action(self) -> None:
        action_type = self.type.currentData()
        if not action_type:
            return
        data: dict[str, Any] = {
            "action_type": action_type,
            "roll": {"num": self.num.value(), "sides": self.sides.value()},
        }
        if self.name.text():
            data["name"] = self.name.text()
        if self.desc.text():
            data["desc"] = self.desc.text()
        card = ActionCard(data, self._remove_card)
        self.cards.addWidget(card)
        self._data.append(data)
        self._clear_form()

    def _remove_card(self, card: ActionCard) -> None:
        idx = self.cards.indexOf(card)
        if idx != -1:
            self._data.pop(idx)
        card.setParent(None)
        card.deleteLater()

    def actions(self) -> list[dict[str, Any]]:
        return list(self._data)


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
        self.action_labels: dict[str, str] | None = None
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
            labels = {
                "type": "Type",
                "num": "Number of Dice",
                "sides": "Die Sides",
                "name": "Name",
                "desc": "Description",
            }
            self.action_labels = labels
            return ActionsEditor(labels)
        return QLabel("(Coming soon)")

    # API -------------------------------------------------------------
    def widgets_for(self, field: str) -> QWidget:
        return self.widgets[field]

    def label_for(self, field: str) -> Any:
        if field == "actions" and self.action_labels is not None:
            return self.action_labels
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
