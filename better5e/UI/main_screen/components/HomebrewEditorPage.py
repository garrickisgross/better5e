from PyQt6.QtWidgets import QLabel

from better5e.UI.core.basepage import BasePage


class HomebrewEditorPage(BasePage):
    """Placeholder homebrew editor page."""

    def __init__(self, app, title: str):
        super().__init__(app, title)
        self.layout().addWidget(QLabel(f"{title} editor coming soon"))
