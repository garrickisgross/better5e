import sys
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PyQt6.QtWidgets import QApplication
import pytest

from better5e.UI.pages.main_screen import MainScreen
from better5e.UI.pages.feature_form_page import FeatureFormPage
from better5e.dao.sqlite import DAO
import better5e.models.game_object as go


@pytest.fixture(scope="session")
def qapp():
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    return app


def test_create_feature_button_pushes_form(qapp):
    pushed: list[object] = []
    app = types.SimpleNamespace(push=lambda w: pushed.append(w), pop=lambda: None)
    screen = MainScreen(app)
    btn_feat = screen.homebrew_panel.layout().itemAt(1).widget()
    btn_feat.click()
    assert pushed and isinstance(pushed[0], FeatureFormPage)


def test_feature_form_valid_submit_persists(qapp):
    dao = DAO()
    grant = go.Feature(name="Grant", desc="g")
    dao.save(grant)
    app = types.SimpleNamespace(push=lambda w: None, pop=lambda: None)
    page = FeatureFormPage(app)
    page.name_edit.setText("Feat")
    page.desc_edit.setPlainText("Some desc")
    page.drop_zone.add_uuid(grant.id, grant.name)
    page.drop_zone.add_uuid(grant.id, grant.name)
    chip = page.drop_zone.layout.itemAt(0).widget()
    chip.click()
    assert page.drop_zone.ids == []
    page.drop_zone.add_uuid(grant.id, grant.name)
    page.uses_edit.setValue(1)
    page.recharge_combo.setCurrentIndex(1)
    assert page.submit_btn.isEnabled()
    page.submit_btn.click()
    saved = [f for f in dao.load_by_kind("feature") if f.name == "Feat"]
    assert saved and saved[0].grants == [grant.id]


def test_feature_form_invalid_missing_desc(qapp):
    dao = DAO()
    before = len(dao.load_by_kind("feature"))
    app = types.SimpleNamespace(push=lambda w: None, pop=lambda: None)
    page = FeatureFormPage(app)
    page.name_edit.setText("Bad")
    assert not page.submit_btn.isEnabled()
    page.submit_btn.click()
    after = len(dao.load_by_kind("feature"))
    assert after == before


def test_actions_and_modifiers_editors(qapp):
    from better5e.UI.components.actions_editor import ActionsEditor
    from better5e.UI.components.modifiers_editor import ModifiersEditor

    ae = ActionsEditor()
    ae.add_card()
    card = ae._cards[0]
    card.name_edit.setText("Hit")
    card.desc_edit.setPlainText("desc")
    card.type_combo.setCurrentIndex(0)
    assert ae.actions()[0].name == "Hit"
    ae.remove_card(card)
    assert ae.actions() == []

    me = ModifiersEditor()
    me.add_row()
    row = me._rows[0]
    row.target_edit.setText("hp")
    row.op_combo.setCurrentIndex(0)
    row.value_spin.setValue(5)
    assert me.modifiers()[0].target == "hp"
    me.remove_row(row)
    assert me.modifiers() == []
