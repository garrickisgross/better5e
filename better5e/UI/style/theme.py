"""Theme application helpers for better5e.

This module converts design tokens into Qt Style Sheet (QSS) and applies
palette tweaks to a :class:`QApplication`.  A small utility for adding drop
shadows to widgets is also provided.
"""

from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Dict

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect

THEME_QSS = Path(__file__).with_name("theme.qss")


def _hex_to_rgb(value: str) -> str:
    """Return ``"R, G, B"`` string from a hex colour value."""

    value = value.lstrip("#")
    r, g, b = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    return f"{r}, {g}, {b}"


def build_qss(tokens: Dict[str, object]) -> str:
    """Generate QSS text for the given tokens."""

    mapping = dict(tokens)
    mapping["accent_rgb"] = _hex_to_rgb(str(tokens["accent"]))
    template = Template(THEME_QSS.read_text(encoding="utf-8"))
    return template.safe_substitute(mapping)


def apply_style(app: QApplication, tokens: Dict[str, object]) -> None:
    """Apply style sheet and palette based on *tokens* to *app*."""

    app.setStyleSheet(build_qss(tokens))

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(str(tokens["bg"])))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(str(tokens["text"])))
    palette.setColor(QPalette.ColorRole.Base, QColor(str(tokens["surface"])))
    palette.setColor(
        QPalette.ColorRole.AlternateBase, QColor(str(tokens["surfaceAlt"]))
    )
    palette.setColor(QPalette.ColorRole.Text, QColor(str(tokens["text"])))
    palette.setColor(QPalette.ColorRole.Button, QColor(str(tokens["surface"])))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(str(tokens["text"])))
    palette.setColor(QPalette.ColorRole.Link, QColor(str(tokens["accent"])))
    palette.setColor(
        QPalette.ColorRole.ToolTipBase, QColor(str(tokens["surfaceAlt"]))
    )
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(str(tokens["text"])))
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.Text,
        QColor(str(tokens["mutedText"])),
    )
    palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.ButtonText,
        QColor(str(tokens["mutedText"])),
    )
    app.setPalette(palette)

    app.setFont(QFont(str(tokens["font_family"]), 13))


def add_shadow(
    widget: QWidget,
    *,
    blur: int = 24,
    x: int = 0,
    y: int = 4,
    color: QColor | None = None,
) -> None:
    """Attach a subtle drop shadow effect to *widget*."""

    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(x, y)
    effect.setColor(color or QColor(0, 0, 0, 80))
    widget.setGraphicsEffect(effect)
