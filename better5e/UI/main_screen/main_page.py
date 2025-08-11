from better5e.UI.basepage import BasePage
from better5e.UI.app import App

from PyQt6.QtWidgets import QLabel, QPushButton

class MainPage(BasePage):
    def __init__(self, app: App):
        super().__init__(app, "Home")
        self.body = self.layout()

        self.body.addWidget(QLabel("Home"))


