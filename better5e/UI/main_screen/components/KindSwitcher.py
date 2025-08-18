from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class KindSwitcher(QWidget):
    """Placeholder widget for switching item kinds."""

    kindChanged = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
