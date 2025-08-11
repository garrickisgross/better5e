from PyQt6.QtWidgets import QListWidget


class RollHistoryPanel(QListWidget):
    """List widget showing past dice rolls."""

    def add_entry(self, text: str) -> None:
        """Append a roll result to the list."""
        self.addItem(text)

    def clear_history(self) -> None:
        """Remove all roll entries."""
        self.clear()
