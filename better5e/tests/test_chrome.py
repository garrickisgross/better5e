import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import os
from PyQt6.QtCore import Qt, QPointF, QEvent
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget
import pytest

from better5e.UI.shell.chrome import FramelessMainWindow
from better5e.UI.style.tokens import gutter


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_chrome_basic_interactions(qapp, monkeypatch):
    win = FramelessMainWindow()
    win.show()
    content = QWidget()
    win.set_content(content)
    new_content = QWidget()
    win.set_content(new_content)

    tb = win.titleBar
    assert tb.btnMin.size().width() == 42 and tb.btnMin.size().height() == 32
    assert tb.btnMin.font().pixelSize() == 16
    assert tb.title.font().pixelSize() == 20
    assert tb.layout().contentsMargins().left() == gutter()
    assert tb.title.contentsMargins().top() == 2
    assert tb.title.indent() == 8

    tb.btnMin.click()
    tb.btnMax.click()
    assert tb.btnMax.text() == "❐"
    tb.btnMax.click()
    assert tb.btnMax.text() == "□"
    tb.btnClose.click()

    dbl = QMouseEvent(
        QEvent.Type.MouseButtonDblClick,
        QPointF(0, 0),
        QPointF(0, 0),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    tb.mouseDoubleClickEvent(dbl)

    press = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(0, 0),
        QPointF(0, 0),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    wh = win.windowHandle()
    if wh is not None:
        monkeypatch.setattr(wh, "startSystemMove", lambda: (_ for _ in ()).throw(Exception("fail")))
    tb.mousePressEvent(press)
    move = QMouseEvent(
        QEvent.Type.MouseMove,
        QPointF(10, 10),
        QPointF(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    tb.mouseMoveEvent(move)
    release = QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        QPointF(10, 10),
        QPointF(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    tb.mouseReleaseEvent(release)

    lay = win._contentHost.layout()
    assert lay.itemAt(0).widget() is new_content
