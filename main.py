import sys

from better5e.UI.core.app import App
from better5e.UI.main_screen.main_screen import MainScreen
from PyQt6.QtWidgets import QApplication



def main () -> int:
    qt = QApplication(sys.argv)
    return App(qt, MainScreen).run()

if __name__ == "__main__":
    raise SystemExit(main())
