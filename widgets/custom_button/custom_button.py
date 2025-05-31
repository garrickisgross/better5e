from PySide6 import QtWidgets, QtCore


class custom_button(QtWidgets.QPushButton):
    def __init__(self, text, parent=None, on_click=None):
        super().__init__(text, parent)

        self.setStyleSheet("font-size: 16px; padding: 10px;")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.clicked.connect(on_click)
        self.setMinimumHeight(60)
