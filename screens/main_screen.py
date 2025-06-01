

from PySide6 import QtWidgets, QtCore
from screens.create_feature import CreateFeature

class  MainScreen(QtWidgets.QWidget):
    def __init__(self, app: QtWidgets.QApplication):
        """Initialize the main screen of the application."""
        super().__init__()
        self.app = app
        self.title = "better5e"

        self.container = QtWidgets.QHBoxLayout(self)
        

        #Left Side Menu TODO: We will eventually add in a dice roller and soundboard here. for now we will just use a placeholder.
        self.leftbar = QtWidgets.QVBoxLayout()
        self.leftbar.addWidget(QtWidgets.QPushButton("Dice Roller (Coming Soon)"))
        self.leftbar.addWidget(QtWidgets.QPushButton("Soundboard (Coming Soon)"))

        # Middle Content
        self.middle_content = QtWidgets.QVBoxLayout()
        self.middle_content.addWidget(QtWidgets.QLabel("Welcome to better5e!"))
        self.middle_content.addWidget(QtWidgets.QLabel("This is the main screen."))
        self.middle_content.addWidget(QtWidgets.QLabel("Right now we are just adding features on the right side."))

        # Right Side Menu

        # Feature screen navigation button.
        feature_button = QtWidgets.QPushButton("Create a Feature")
        feature_button.clicked.connect(lambda: self.app.push_widget(CreateFeature))
        
        
        self.rightbar = QtWidgets.QVBoxLayout()
        self.rightbar.addWidget(QtWidgets.QPushButton("Create a Character (Coming Soon)"))
        self.rightbar.addWidget(QtWidgets.QPushButton("Create a Campaign (Coming Soon)"))
        self.rightbar.addWidget(QtWidgets.QPushButton("Create a Monster (Coming Soon)"))
        self.rightbar.addWidget(QtWidgets.QPushButton("Create an Item (Coming Soon)"))
        self.rightbar.addWidget(QtWidgets.QPushButton("Create a Spell (Coming Soon)"))
        self.rightbar.addWidget(QtWidgets.QPushButton("Create a Class (Coming Soon)"))
        self.rightbar.addWidget(feature_button)

        
        
        self.container.addLayout(self.leftbar)
        self.container.addLayout(self.middle_content)
        self.container.addLayout(self.rightbar)
        self.setLayout(self.container)

    