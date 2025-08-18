from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit


class SchemaFormBuilder(QWidget):
    """Very small form builder based on a JSON schema."""

    changed = pyqtSignal()

    def __init__(self, schema: dict, exclude: set[str] | None = None):
        super().__init__()
        self._schema = schema
        self._exclude = exclude or set()
        self._required = set(schema.get("required", []))
        layout = QFormLayout(self)
        self._fields: dict[str, QLineEdit] = {}
        for name, prop in schema.get("properties", {}).items():
            if name in self._exclude or name in {"id", "kind"}:
                continue
            w = QLineEdit()
            w.textChanged.connect(self.changed.emit)
            layout.addRow(self.label_for(name), w)
            self._fields[name] = w

    def values(self) -> dict:
        return {name: w.text() for name, w in self._fields.items() if w.text()}

    def set_value(self, name: str, value: str) -> None:
        if name in self._fields:
            self._fields[name].setText(value)

    def is_valid(self) -> bool:
        for name in self._required:
            if name in self._fields and not self._fields[name].text().strip():
                return False
        return True

    @staticmethod
    def label_for(name: str) -> str:
        return name.replace("_", " ").title()
