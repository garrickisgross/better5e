import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import QApplication, QWidget
import pytest

from better5e.UI.style import tokens
from better5e.UI.style import theme


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_tokens_dark_and_light():
    dark = tokens.dark()
    light = tokens.light()
    assert dark["bg"] == "#0f1115"
    assert light["bg"] == "#ffffff"
    assert "font_mono" in dark


def test_build_and_apply_style(qapp):
    t = tokens.dark()
    qss = theme.build_qss(t)
    assert "QMainWindow" in qss
    theme.apply_style(qapp, t)
    assert qapp.styleSheet() == qss


def test_add_shadow(qapp):
    w = QWidget()
    theme.add_shadow(w)
    assert w.graphicsEffect() is not None
