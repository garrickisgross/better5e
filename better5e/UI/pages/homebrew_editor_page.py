"""Base infrastructure for homebrew editing pages.

This module provides a minimal header with Back and Save buttons. Subclasses
are expected to extend the page by adding their own form content beneath this
header.
"""

from PyQt6.QtWidgets import QHBoxLayout, QPushButton

from better5e.UI.core.basepage import BasePage


class HomebrewEditorPage(BasePage):
    """Basic shell for homebrew editing pages.

    The page renders a simple header containing Back and Save buttons. The Save
    button is exposed via :pyattr:`save_btn` so that child classes can control
    its enabled state or connect additional callbacks.
    """

    def __init__(self, app, title: str) -> None:
        super().__init__(app, title)
        layout = self.layout()

        header = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.app.pop)
        self.save_btn = QPushButton("Save")
        self.save_btn.setEnabled(False)
        header.addWidget(back_btn)
        header.addWidget(self.save_btn)
        header.addStretch(1)
        layout.addLayout(header)
