from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from better5e.UI.core.basepage import BasePage


class HomebrewEditorPage(BasePage):
    """Basic shell for homebrew editing pages."""

    def __init__(self, app, title: str) -> None:
        super().__init__(app, title)
        layout = self.layout()

        header = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.app.pop)
        save_btn = QPushButton("Save")
        save_btn.setEnabled(False)
        header.addWidget(back_btn)
        header.addWidget(save_btn)
        header.addStretch(1)
        layout.addLayout(header)

        placeholder = QLabel(f"{title} editor coming soon")
        placeholder.setObjectName("Placeholder")
        layout.addWidget(placeholder)
