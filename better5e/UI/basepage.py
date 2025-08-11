from PyQt6.QtWidgets import QWidget, QVBoxLayout
from better5e.UI.app import App

class BasePage(QWidget):
    def __init__(self, app: App, title: str):
        super().__init__()
        self.app = app
        self.setObjectName(title)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(24, 24, 24, 24)
    