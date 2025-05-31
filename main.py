import sys
import random
from PySide6 import QtWidgets, QtCore, QtGui

from screens.main_screen.main_screen import MainScreen

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = MainScreen()
    widget.show()
    sys.exit(app.exec())
   

if __name__ == "__main__":
    main()