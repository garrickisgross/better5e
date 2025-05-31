from PySide6 import QtWidgets, QtCore
from widgets.custom_button.custom_button import custom_button
from controllers.main_screen_right_panel_controller import MainScreenRightPanelController

class MainScreenRightPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.controller = MainScreenRightPanelController()
        self.container = QtWidgets.QVBoxLayout(self)
        self.container.setContentsMargins(2,2,2,2)
        self.container.setSpacing(2)
        self.alignment = QtCore.Qt.AlignmentFlag.AlignCenter
        self.setLayout(self.container)

        self.container.addWidget(custom_button("Create A Class", self, self.controller.create_class))
        self.container.addWidget(custom_button("Create A Feature", self, self.controller.create_feature))
        self.container.addWidget(custom_button("Create An Item", self, self.controller.create_item))
        self.container.addWidget(custom_button("Create A Weapon", self, self.controller.create_weapon))
        self.container.addWidget(custom_button("Create A Spell", self, self.controller.create_spell))




