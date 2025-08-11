import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import QApplication, QWidget
import pytest

from better5e.UI.core.app import App


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_app_stack_and_run(qapp, monkeypatch):
    def factory(app):
        return QWidget()

    app = App(qapp, factory)

    w2 = QWidget()
    app.push(w2)
    assert app.stack[-1] is w2

    app.pop()
    assert app.stack[-1] is not w2

    app.pop()  # no effect when one item
    assert len(app.stack) == 1

    app._add_if_needed(app.stack[0])  # widget already added

    app.stack.clear()
    app._update_title()

    monkeypatch.setattr(qapp, "exec", lambda: 1)
    assert app.run() == 1
