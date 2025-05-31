from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Slot

from widgets.main_screen.right_panel.right_panel import MainScreenRightPanel

class  MainScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Main Screen"
        self.description = "This is the main screen of the application"

        self.container = QtWidgets.QHBoxLayout(self)
        
        self.left_panel = QtWidgets.QVBoxLayout()
        self.right_panel = QtWidgets.QVBoxLayout()
        self.middle_panel = QtWidgets.QVBoxLayout()
        self.container.addLayout(self.left_panel)
        self.container.addLayout(self.middle_panel)
        self.container.addLayout(self.right_panel)
        self.setWindowTitle(self.title)
        
        self.middle_panel.addWidget(QtWidgets.QLabel(self.description))
        self.left_panel.addWidget(QtWidgets.QLabel("Left Panel"))
        self.right_panel.addWidget(MainScreenRightPanel())
       

    