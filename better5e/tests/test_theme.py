from pathlib import Path


def test_center_scroll_theme_scope():
    theme = Path(__file__).resolve().parents[1] / "UI/style/theme.qss"
    text = theme.read_text()
    assert "QScrollArea#CenterScroll QWidget," not in text
    assert "QScrollArea#CenterScroll QWidget#qt_scrollarea_viewport" in text
