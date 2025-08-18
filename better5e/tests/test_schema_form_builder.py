from PyQt6.QtWidgets import QApplication, QComboBox, QLineEdit, QSpinBox, QTextEdit

from better5e.models.game_object import Feature
from better5e.UI.components.grant_picker import GrantPicker
from better5e.UI.components.list_editor import ListEditor
from better5e.UI.core.schema_form_builder import SchemaFormBuilder

app = QApplication([])


def test_builder_selects_widgets():
    builder = SchemaFormBuilder({"desc": {"multiline": True}})
    widgets = {
        name: builder.build_widget(name, field.annotation)
        for name, field in Feature.model_fields.items()
    }

    assert isinstance(widgets["name"], QLineEdit)
    assert isinstance(widgets["desc"], QTextEdit)
    assert isinstance(widgets["uses_max"], QSpinBox)
    assert widgets["uses_max"].specialValueText() == ""
    assert isinstance(widgets["recharge"], QComboBox)
    assert widgets["recharge"].itemText(0) == ""
    assert isinstance(widgets["actions"], ListEditor)
    assert isinstance(widgets["grants"], GrantPicker)
