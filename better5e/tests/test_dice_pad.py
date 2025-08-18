import os
import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QMouseEvent, QWheelEvent
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from better5e.UI.components.die_button import DieButton
from better5e.UI.components.dice_options import DiceOptionsPanel, ModifierControl


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _mouse_press(btn: DieButton, button: Qt.MouseButton) -> None:
    ev = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(),
        QPointF(),
        button,
        button,
        Qt.KeyboardModifier.NoModifier,
    )
    btn.mousePressEvent(ev)


def test_die_button_interactions(qapp):
    btn = DieButton(6)
    assert btn.count == 0
    _mouse_press(btn, Qt.MouseButton.LeftButton)
    assert btn.count == 1 and not btn.badge.isHidden()
    _mouse_press(btn, Qt.MouseButton.RightButton)
    assert btn.count == 0 and btn.badge.isHidden()
    _mouse_press(btn, Qt.MouseButton.MiddleButton)
    assert btn.count == 0
    wheel_up = QWheelEvent(
        QPointF(),
        QPointF(),
        QPoint(),
        QPoint(0, 120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    btn.wheelEvent(wheel_up)
    assert btn.count == 1
    wheel_down = QWheelEvent(
        QPointF(),
        QPointF(),
        QPoint(),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    btn.wheelEvent(wheel_down)
    assert btn.count == 0
    wheel_zero = QWheelEvent(
        QPointF(),
        QPointF(),
        QPoint(),
        QPoint(0, 0),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    btn.wheelEvent(wheel_zero)
    assert btn.count == 0
    btn.count = 10
    assert btn.badge.text() == "9+"


def test_modifier_control(qapp):
    ctrl = ModifierControl()
    values = []
    ctrl.valueChanged.connect(values.append)
    ctrl.setValue(5)
    ctrl.minus.click()
    ctrl.plus.click()
    ctrl.setValue(1000)
    ctrl.edit.setText("abc")
    assert ctrl.value == 0
    assert values[0] == 5


def test_notation_and_state(qapp):
    panel = DiceOptionsPanel()
    assert not panel.roll_btn.isEnabled()
    panel.die_buttons[8].count = 2
    panel.mod_ctrl.setValue(-5)
    assert panel.roll_btn.isEnabled()
    assert panel.get_notation() == "2d8 - 5"
    assert panel.state() == ({8: 2}, -5)
    panel.reset()
    assert panel.get_notation() == ""
    assert not panel.roll_btn.isEnabled()
    panel.roll()  # no dice selected: early return
