import sys

from better5e.UI.app import App
from better5e.UI.main_screen.main_page import MainPage
from PyQt6.QtWidgets import QApplication



def main () -> int:
    qt = QApplication(sys.argv)
    return App(qt, MainPage).run()

if __name__ == "__main__":
    raise SystemExit(main())
