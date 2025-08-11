import sys
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import random

from PyQt6.QtWidgets import QApplication
import pytest

from better5e.UI.main_screen.components.roll_history import RollHistoryPanel
from better5e.UI.main_screen.components.dice_options import DiceOptionsPanel
from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.main_screen.components.card_grid import CardGrid
from better5e.UI.main_screen.components.homebrew_panel import HomebrewPanel
from better5e.UI.main_screen.main_screen import MainScreen


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dice_roll_updates_history(qapp, monkeypatch):
    history = RollHistoryPanel()
    dice = DiceOptionsPanel()
    dice.rollMade.connect(history.add_entry)
    dice.die_box.setCurrentText("d4")
    dice.count_spin.setValue(2)
    dice.mod_spin.setValue(3)
    seq = iter([1, 2])
    monkeypatch.setattr(random, "randint", lambda a, b: next(seq))
    dice.roll()
    assert history.count() == 1
    assert history.item(0).text() == "2d4+3 = 6 (1, 2)"
    history.clear_history()
    assert history.count() == 0


def test_section_header_and_card_grid(qapp):
    emitted = []
    header = SectionHeader("Title")
    header.seeAll.connect(lambda: emitted.append(True))
    header.button.click()
    assert emitted == [True]

    grid = CardGrid(["A", "B", "C"])
    assert grid.layout().count() == 3


def test_homebrew_panel_signals(qapp):
    panel = HomebrewPanel()
    received = []
    panel.openHomebrew.connect(received.append)
    # trigger first button
    btn = panel.layout().itemAt(0).widget()
    btn.click()
    assert received == ["feature"]


def test_main_screen_signal_propagation(qapp, monkeypatch):
    app = types.SimpleNamespace()
    screen = MainScreen(app)

    signals = []
    screen.seeAllCharacters.connect(lambda: signals.append("see_chars"))
    screen.createNewCharacter.connect(lambda: signals.append("new_char"))
    screen.seeAllCampaigns.connect(lambda: signals.append("see_camps"))
    screen.createNewCampaign.connect(lambda: signals.append("new_camp"))
    screen.openHomebrew.connect(lambda kind: signals.append(kind))

    screen.characters_header.button.click()
    screen.characters_create.click()
    screen.campaigns_header.button.click()
    screen.campaigns_create.click()
    hb_btn = screen.homebrew_panel.layout().itemAt(1).widget()
    hb_btn.click()

    assert signals == ["see_chars", "new_char", "see_camps", "new_camp", "class"]

    # roll wiring
    seq = iter([4])
    monkeypatch.setattr(random, "randint", lambda a, b: next(seq))
    screen.dice_panel.count_spin.setValue(1)
    screen.dice_panel.mod_spin.setValue(0)
    screen.dice_panel.die_box.setCurrentText("d6")
    screen.dice_panel.roll()
    assert screen.roll_history.count() == 1
