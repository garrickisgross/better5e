from better5e.UI.core.basepage import BasePage
from better5e.UI.core.app import App

from PyQt6.QtWidgets import QLabel, QPushButton

class MainScreen(BasePage):
    def __init__(self, app: App):
        super().__init__(app, "Home")
        self.body = self.layout()

        self.body.addWidget(QLabel("Home"))


