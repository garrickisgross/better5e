from typing import Callable, Union

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget

WidgetFactory = Callable[["App"], QWidget]


class App:
    """Simple stack-based application window."""

    def __init__(self, app: QApplication, main: Union[QWidget, WidgetFactory]):
        self.app = app
        self.stack: list[QWidget] = []
        self.window = QMainWindow()
        self.window.setWindowTitle("better5e")
        self.window.resize(520, 320)

        self._stacked = QStackedWidget()
        self.window.setCentralWidget(self._stacked)

        first = main(self) if callable(main) else main
        self.push(first)
        self.window.show()

    def push(self, widget: QWidget) -> None:
        self._add_if_needed(widget)
        self._stacked.setCurrentWidget(widget)
        self.stack.append(widget)
        self._update_title()

    def pop(self) -> None:
        if len(self.stack) <= 1:
            return
        current = self.stack.pop()
        self._stacked.removeWidget(current)
        current.deleteLater()
        self._stacked.setCurrentWidget(self.stack[-1])
        self._update_title()

    def _add_if_needed(self, widget: QWidget) -> None:
        if self._stacked.indexOf(widget) == -1:
            self._stacked.addWidget(widget)

    def _update_title(self) -> None:
        name = type(self.stack[-1]).__name__ if self.stack else "better5e"
        self.window.setWindowTitle(f"better5e - {name}")

    def run(self) -> int:
        """Start the Qt event loop."""
        return self.app.exec()
