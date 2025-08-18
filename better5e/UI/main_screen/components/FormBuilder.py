from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class FormBuilder(QWidget):
    """Placeholder schema-driven form builder."""

    dirtyChanged = pyqtSignal(bool)
    valueChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
