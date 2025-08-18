import os
import types
from uuid import uuid4

import pytest
from PyQt6.QtWidgets import QApplication

from better5e.UI.main_screen.components.homebrew_panel import HomebrewPanel
from better5e.UI.main_screen.create_pages.CreatePage import CreatePage
import importlib
create_page_mod = importlib.import_module(
    "better5e.UI.main_screen.create_pages.CreatePage"
)
from better5e.dao import sqlite


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_homebrew_buttons_open_pages(qapp):
    pushed: list[CreatePage] = []
    app = types.SimpleNamespace(push=lambda w: pushed.append(w), pop=lambda: None)
    panel = HomebrewPanel(app)
    kinds = [
        "Feature",
        "Class",
        "Subclass",
        "Item",
        "Spellcasting",
        "Spell",
        "Race",
        "Background",
    ]
    for idx, kind in enumerate(kinds, start=1):
        btn = panel.layout().itemAt(idx).widget()
        btn.click()
        assert isinstance(pushed[idx - 1], CreatePage)
        assert pushed[idx - 1].kind == kind


def test_create_page_builds_form_and_relations(qapp):
    app = types.SimpleNamespace(pop=lambda: None, push=lambda w: None)
    page = CreatePage(app, "Feature")
    assert {"name", "desc"}.issubset(page.form._fields.keys())
    assert "grants" in page.relations
    spell_page = CreatePage(app, "Spell")
    assert "name" in spell_page.form._fields


def test_create_page_validation_and_submit(qapp, monkeypatch):
    saved = []
    monkeypatch.setattr(
        create_page_mod, "DAO", lambda: types.SimpleNamespace(save=lambda obj: saved.append(obj))
    )
    app = types.SimpleNamespace(pop=lambda: None, push=lambda w: None)
    page = CreatePage(app, "Feature")
    assert not page.create_btn.isEnabled()
    uid = uuid4()
    page.relations["grants"].add_uuid(uid)
    page.form.set_value("name", "Feat")
    page.form.set_value("desc", "Desc")
    page._update_valid()
    assert page.create_btn.isEnabled()
    page._submit()
    assert saved and saved[0].grants == [uid]


def test_drop_zone_remove_and_unknown_submit(qapp, monkeypatch):
    dz = create_page_mod.DropZone()
    uid = uuid4()
    dz.add_uuid(uid)
    dz.remove_uuid(uid)
    assert dz.values() == []

    app = types.SimpleNamespace(pop=lambda: None, push=lambda w: None)
    page = CreatePage(app, "Feature")
    page._submit()  # invalid, should no-op
    page.form.set_value("name", "Feat")
    page.form.set_value("desc", "Desc")
    page._update_valid()
    page.kind = "Mystery"
    called = []
    monkeypatch.setattr(create_page_mod, "DAO", lambda: types.SimpleNamespace(save=lambda obj: called.append(obj)))
    page._submit()
    assert called == []
