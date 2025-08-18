"""Create Feature page.

This is a very small but functional implementation that demonstrates how the
application could build forms from the :class:`~better5e.models.game_object.Feature`
model.  It is intentionally minimalist: the goal of this repository exercise is
to showcase the schema driven form builder and list editor rather than a full
featured editor.
"""

from PyQt6.QtWidgets import QFormLayout

from better5e.models.game_object import Feature
from better5e.UI.core.schema_form_builder import SchemaFormBuilder
from better5e.UI.pages.homebrew_editor_page import HomebrewEditorPage


class CreateFeaturePage(HomebrewEditorPage):
    """Simple page allowing creation of a :class:`Feature` instance."""

    def __init__(self, app) -> None:
        super().__init__(app, "Create Feature")

        # Construct widgets based on the Feature schema. Only a subset of fields
        # are required for the tests; the builder handles basic types.
        hints = {"desc": {"multiline": True}}
        builder = SchemaFormBuilder(hints)

        form = QFormLayout()
        self.fields = {}
        for name, field in Feature.model_fields.items():
            widget = builder.build_widget(name, field.annotation)
            form.addRow(name, widget)
            self.fields[name] = widget

        self.layout().addLayout(form)
