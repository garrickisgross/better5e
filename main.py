import sys

from PyQt6.QtWidgets import QApplication

from better5e.UI.core.app import App
from better5e.UI.pages.main_screen import MainScreen
from better5e.UI.core.style import tokens
from better5e.UI.core.style.theme import apply_style



def main() -> int:
    qt = QApplication(sys.argv)
    apply_style(qt, tokens.dark())
    return App(qt, MainScreen).run()

if __name__ == "__main__":
    raise SystemExit(main())
