import types
from uuid import UUID

from PyQt6.QtWidgets import QApplication, QToolButton, QLabel
from PyQt6.QtCore import QMimeData, Qt
import pytest
import os

from better5e.UI.homebrew.schema_form import SchemaFormBuilder, ValidationErrorUI
from better5e.UI.homebrew.dnd import DropZone, mime_from_record, parse_mime, Record
from better5e.UI.homebrew.feature_create_page import FeatureCreatePage
from better5e.dao.sqlite import DAO
from better5e.models.game_object import Feature
from better5e.models.enums import RechargeType, ActionType


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_form_builder_validation(qapp):
    form = SchemaFormBuilder(Feature)
    assert form.label_for("uses_max") == "Maximum Uses"
    labels = form.label_for("actions")
    assert labels["type"] == "Type"
    with pytest.raises(ValidationErrorUI):
        form.get_payload()
    form.widgets_for("name").setText("Feat")
    form.widgets_for("desc").setPlainText("desc")
    form.widgets_for("uses_max").setValue(3)
    form.widgets_for("recharge").setCurrentIndex(1)
    actions = form.widgets_for("actions")
    actions._add_action()  # cover early return when type not selected
    actions.type.setCurrentIndex(1)
    actions.num.setValue(1)
    actions.sides.setValue(6)
    actions.name.setText("Swing")
    actions.desc.setText("Hard")
    actions._add_action()
    assert actions.cards.count() == 1
    card = actions.cards.itemAt(0).widget()
    texts = {w.text() for w in card.findChildren(QLabel)}
    assert {"Swing", "Action", "Hard", "1d6"} <= texts
    card.findChild(QToolButton).click()
    assert actions.cards.count() == 0
    actions.type.setCurrentIndex(1)
    actions.name.setText("Swing")
    actions.desc.setText("Hard")
    actions._add_action()
    payload = form.get_payload()
    assert payload["uses_max"] == 3
    assert payload["recharge"] == RechargeType.LONG_REST.value
    act = payload["actions"][0]
    assert act["name"] == "Swing"
    assert act["desc"] == "Hard"


def test_dropzone_dnd_and_remove(qapp):
    dz = DropZone(["feature"], multi=True)
    rec = Record(uuid=UUID(int=1), kind="feature", name="F1")
    mime = mime_from_record(rec)

    class DummyEvt:
        def __init__(self, md):
            self._md = md
            self.accepted = False
        def mimeData(self):
            return self._md
        def acceptProposedAction(self):
            self.accepted = True
    evt = DummyEvt(mime)
    dz.dragEnterEvent(evt)
    assert evt.accepted
    evt2 = DummyEvt(mime)
    dz.dropEvent(evt2)
    assert dz.uuids() == [rec.uuid]
    chip = dz._layout.itemAt(0).widget()
    btn = chip.findChild(QToolButton)
    btn.click()
    assert dz.uuids() == []

    # parse_mime fallback
    class DummyEvt2:
        def mimeData(self):
            return QMimeData()
    assert parse_mime(DummyEvt2()) is None

    # acceptance rules
    dz_bad = DropZone(["feature"], multi=False)
    dz_bad.add_record(Record(uuid=UUID(int=5), kind="class", name="bad"))
    assert dz_bad.uuids() == []
    dz_bad.add_record(rec)
    dz_dup = DropZone(["feature"], multi=True)
    dz_dup.add_record(rec)
    dz_dup.add_record(rec)  # duplicate triggers check
    assert dz_dup.uuids() == [rec.uuid]
    dz_bad.add_record(Record(uuid=UUID(int=6), kind="feature", name="F2"))
    assert dz_bad.uuids() == [rec.uuid]


def test_feature_create_submit(qapp, monkeypatch):
    class DummyApp:
        def __init__(self):
            self.popped = False
        def pop(self):
            self.popped = True
        def push(self, w):
            pass

    app = DummyApp()
    page = FeatureCreatePage(app)
    page.form_builder.widgets_for("name").setText("Feat")
    page.form_builder.widgets_for("desc").setPlainText("desc")
    page.form_builder.widgets_for("uses_max").setValue(2)
    page.form_builder.widgets_for("recharge").setCurrentIndex(1)
    act_editor = page.form_builder.widgets_for("actions")
    act_editor.type.setCurrentIndex(1)
    act_editor.num.setValue(1)
    act_editor.sides.setValue(6)
    act_editor.name.setText("Hit")
    act_editor.desc.setText("Hard")
    act_editor._add_action()
    assert act_editor.cards.count() == 1
    card = act_editor.cards.itemAt(0).widget()
    texts = {w.text() for w in card.findChildren(QLabel)}
    assert {"Hit", "Action", "Hard", "1d6"} <= texts
    act_editor.type.setCurrentIndex(1)
    act_editor.name.setText("Kick")
    act_editor.desc.setText("Soft")
    act_editor._add_action()
    assert act_editor.cards.count() == 2
    card2 = act_editor.cards.itemAt(1).widget()
    texts2 = {w.text() for w in card2.findChildren(QLabel)}
    assert {"Kick", "Action", "Soft", "1d20"} <= texts2
    rec = Record(uuid=UUID(int=2), kind="class", name="C1")
    page.grants.add_record(rec)
    saved = {}
    monkeypatch.setattr(DAO, "save", lambda self, obj: saved.setdefault("obj", obj))
    page.on_submit()
    obj = saved["obj"]
    assert obj.name == "Feat"
    assert obj.uses_max == 2
    assert obj.recharge == RechargeType.LONG_REST
    assert obj.actions[0].name == "Hit"
    assert obj.actions[0].desc == "Hard"
    assert len(obj.actions) == 2
    assert obj.grants == [rec.uuid]
    assert app.popped


def test_feature_create_submit_validation(qapp):
    app = types.SimpleNamespace(pop=lambda: None, push=lambda w: None)
    page = FeatureCreatePage(app)
    page.form_builder.widgets_for("name").setText("Feat")
    page.on_submit()
    assert page.error_label.text() == "invalid"


def test_feature_create_tab_layout_and_dnd(qapp):
    class DummyApp:
        def pop(self):
            pass
        def push(self, w):
            pass

    dao = DAO()
    feat = Feature(name="Fcat", desc="d")
    dao.save(feat)
    page = FeatureCreatePage(DummyApp())
    assert [page.tabs.tabText(i) for i in range(page.tabs.count())] == [
        "Info",
        "Actions",
        "Modifier",
        "Grants",
    ]
    info_tab = page.tabs.widget(0)
    actions_tab = page.tabs.widget(1)
    assert page.form_builder.widgets_for("uses_max").parent() == info_tab
    assert page.form_builder.widgets_for("recharge").parent() == info_tab
    assert page.form_builder.widgets_for("actions").parent() == actions_tab
    assert page.catalog_tabs.isHidden()
    page.tabs.setCurrentIndex(page._grants_index)
    assert not page.catalog_tabs.isHidden()
    list_widget = page.catalog_tabs.widget(0)
    item = list_widget.item(0)
    rec = item.data(Qt.ItemDataRole.UserRole)
    page.grants.add_record(rec)
    assert page.grants.uuids() == [rec.uuid]
