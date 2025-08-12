from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QListWidget

from better5e.UI.style import tokens


class RollHistoryPanel(QListWidget):
    """List widget showing past dice rolls."""

    def __init__(self) -> None:
        super().__init__()
        self.setFont(QFont(tokens.dark()["font_mono"], 12))
        self.setAlternatingRowColors(True)

    def add_entry(self, text: str) -> None:
        """Append a roll result to the list."""
        self.addItem(text)

    def clear_history(self) -> None:
        """Remove all roll entries."""
        self.clear()
