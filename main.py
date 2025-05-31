import sys
import random
from PySide6 import QtWidgets, QtCore, QtGui

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
    
        self.hello = ["Hello Welt", "Hei maailma", "Hola mundo", "Bonjour le monde", "Ciao mondo"]

        self.button = QtWidgets.QPushButton("Click ME!")
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))


def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = MyWidget()
    widget.resize(800, 600)
    widget.setWindowTitle("Hello World App")
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()