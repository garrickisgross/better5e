import sys
from PySide6 import QtWidgets, QtCore, QtGui

from PySide6.QtWidgets import QApplication
from screens.main_screen import MainScreen

class App(QApplication):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.main_window = QtWidgets.QMainWindow()
        self.main_window.setGeometry(100, 100, 1080, 720)


    def push_widget(self, widget: QtWidgets.QWidget.__class__):
        """Push a widget to the application stack."""
        self.stack.insert(0, widget)
        new_widget = widget(app=self)
        self.main_window.setCentralWidget(new_widget)
        self.main_window.setWindowTitle(new_widget.title)
    
    def pop_widget(self):
        """Pop the top widget from the application stack."""
        if len(self.stack) > 1:
            self.stack.pop(0)
            widget_class = self.stack[0]
            widget = widget_class(app=self)
            self.main_window.setCentralWidget(widget)
            self.main_window.setWindowTitle(widget.title)
    

def main():
    app = App()
    app.push_widget(MainScreen)
    app.main_window.show()
    sys.exit(app.exec())
   

if __name__ == "__main__":
    main()