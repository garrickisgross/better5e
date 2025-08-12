import sys
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import os
import random
from datetime import datetime

from PyQt6.QtWidgets import QApplication, QMenu
import pytest

from better5e.UI.main_screen.components.roll_history import RollHistoryPanel
from better5e.UI.main_screen.components.dice_options import DiceOptionsPanel
from better5e.UI.main_screen.components.section_header import SectionHeader
from better5e.UI.main_screen.components.card_grid import CardGrid
from better5e.UI.main_screen.components.homebrew_panel import HomebrewPanel
from better5e.UI.main_screen.main_screen import MainScreen


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dice_roll_updates_history(qapp, monkeypatch):
    history = RollHistoryPanel()
    history.add_entry("bad")
    assert history.count() == 0
    dice = DiceOptionsPanel()
    dice.rollMade.connect(history.add_entry)
    dice.die_box.setCurrentText("d4")
    dice.count_spin.setValue(2)
    dice.mod_spin.setValue(3)
    seq = iter([1, 2])
    monkeypatch.setattr(random, "randint", lambda a, b: next(seq))
    dice.roll()
    assert history.count() == 1
    item = history.item(0)
    card = history.itemWidget(item)
    assert card.notation_label.text() == "2d4+3"
    assert card.total_label.text() == "6"
    assert [lab.text() for lab in card.roll_labels] == ["1", "2"]
    history.clear_history()
    assert history.count() == 0


def test_roll_history_context_and_reroll(qapp, monkeypatch):
    history = RollHistoryPanel()
    history.add_entry("1d20+0 = 20 (20)")
    item = history.item(0)
    card = history.itemWidget(item)
    assert card.property("crit") is True

    history.show()
    qapp.processEvents()
    pos = history.visualItemRect(item).center()

    def fake_exec_copy(menu, _):
        return menu.actions()[0]

    monkeypatch.setattr(QMenu, "exec", fake_exec_copy)
    history._show_context_menu(pos)
    assert QApplication.clipboard().text() == "1d20+0 = 20 (20)"

    seq = iter([5])
    monkeypatch.setattr(random, "randint", lambda a, b: next(seq))
    history._reroll_item(item)
    assert history.count() == 2

    def fake_exec_delete(menu, _):
        return menu.actions()[1]

    monkeypatch.setattr(QMenu, "exec", fake_exec_delete)
    history._show_context_menu(pos)
    assert history.count() == 1

    def fake_exec_clear(menu, _):
        return menu.actions()[3]

    monkeypatch.setattr(QMenu, "exec", fake_exec_clear)
    history._show_context_menu(pos)
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


def test_fmt_time_variants():
    from better5e.UI.main_screen.components.roll_history import _fmt_time

    now = datetime.now()
    assert ":" in _fmt_time(now)

    same_year = datetime(now.year, 8, 11, 19, 12)
    if same_year.date() == now.date():
        same_year = datetime(now.year, 8, 12, 19, 12)
    assert "·" in _fmt_time(same_year)

    other_year = datetime(now.year - 1, 8, 11, 19, 12)
    assert "," in _fmt_time(other_year)
