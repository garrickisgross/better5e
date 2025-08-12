import types
from uuid import UUID

from PyQt6.QtWidgets import QApplication, QToolButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QMimeData
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
    with pytest.raises(ValidationErrorUI):
        form.get_payload()
    form.widgets_for("name").setText("Feat")
    form.widgets_for("uses_max").setValue(3)
    form.widgets_for("recharge").setCurrentIndex(1)
    actions = form.widgets_for("actions")
    row1 = actions.rows.itemAt(0).widget()
    row1._remove()  # cover remove path
    actions.rows.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
    actions._add_row()
    row2 = actions.rows.itemAt(actions.rows.count() - 1).widget()
    row2.type.setCurrentIndex(1)
    payload = form.get_payload()
    assert payload["uses_max"] == 3
    assert payload["recharge"] == RechargeType.LONG_REST.value
    assert payload["actions"][0]["action_type"] == ActionType.ACTION.value


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
    page.form_builder.widgets_for("uses_max").setValue(2)
    page.form_builder.widgets_for("recharge").setCurrentIndex(1)
    act_editor = page.form_builder.widgets_for("actions")
    row = act_editor.rows.itemAt(0).widget()
    row.type.setCurrentIndex(1)
    row.num.setValue(1)
    row.sides.setValue(6)
    rec = Record(uuid=UUID(int=2), kind="class", name="C1")
    page.grants.add_record(rec)
    saved = {}
    monkeypatch.setattr(DAO, "save", lambda self, obj: saved.setdefault("obj", obj))
    page.on_submit()
    obj = saved["obj"]
    assert obj.name == "Feat"
    assert obj.uses_max == 2
    assert obj.recharge == RechargeType.LONG_REST
    assert obj.actions[0].action_type == ActionType.ACTION
    assert obj.grants == [rec.uuid]
    assert app.popped


def test_feature_create_submit_validation(qapp):
    app = types.SimpleNamespace(pop=lambda: None, push=lambda w: None)
    page = FeatureCreatePage(app)
    page.on_submit()
    assert page.error_label.text() == "invalid"
