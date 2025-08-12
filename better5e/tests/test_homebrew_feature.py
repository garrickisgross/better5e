import types
from uuid import UUID

from PyQt6.QtWidgets import QApplication, QToolButton
from PyQt6.QtCore import QMimeData
import pytest
import os

from better5e.UI.homebrew.schema_form import SchemaFormBuilder, ValidationErrorUI
from better5e.UI.homebrew.dnd import DropZone, mime_from_record, parse_mime, Record
from better5e.UI.homebrew.feature_create_page import FeatureCreatePage
from better5e.dao.sqlite import DAO
from better5e.models.game_object import Feature


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_schema_form_builder_validation(qapp):
    form = SchemaFormBuilder(Feature)
    with pytest.raises(ValidationErrorUI):
        form.get_payload()
    form.widgets_for("name").setText("Feat")
    payload = form.get_payload()
    assert payload["name"] == "Feat"


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
    rec = Record(uuid=UUID(int=2), kind="class", name="C1")
    page.grants.add_record(rec)
    saved = {}
    monkeypatch.setattr(DAO, "save", lambda self, obj: saved.setdefault("obj", obj))
    page.on_submit()
    assert saved["obj"].name == "Feat"
    assert saved["obj"].grants == [rec.uuid]
    assert app.popped


def test_feature_create_submit_validation(qapp):
    app = types.SimpleNamespace(pop=lambda: None, push=lambda w: None)
    page = FeatureCreatePage(app)
    page.on_submit()
    assert page.error_label.text() == "invalid"
