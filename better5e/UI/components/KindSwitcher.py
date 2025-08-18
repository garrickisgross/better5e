from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox


class KindSwitcher(QComboBox):
    """Dropdown to select a homebrew kind."""

    kindChanged = pyqtSignal(str)

    def __init__(self, kinds: list[str], parent=None) -> None:
        super().__init__(parent)
        self.addItems(kinds)
        self.currentTextChanged.connect(self.kindChanged.emit)
