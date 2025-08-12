from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QSplitter,
    QScrollArea,
    QFrame,
    QFormLayout,
    QTabWidget,
    QPushButton,
    QVBoxLayout,
)

from better5e.UI.core.basepage import BasePage
from better5e.UI.homebrew.schema_form import SchemaFormBuilder, ValidationErrorUI
from better5e.UI.homebrew.dnd import CatalogList, Record, DropZone
from better5e.dao.sqlite import DAO
from better5e.models.game_object import Feature


class FeatureCreatePage(BasePage):
    """Page for creating a Feature object."""

    def __init__(self, app):
        super().__init__(app, "Create Feature")
        root = self.layout()

        # header -------------------------------------------------------
        header = QHBoxLayout()
        back = QToolButton()
        back.setText("Back")
        back.clicked.connect(self.app.pop)
        title = QLabel("Create Feature")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(back)
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        # body ---------------------------------------------------------
        splitter = QSplitter()
        root.addWidget(splitter, 1)

        # left form
        self.form_builder = SchemaFormBuilder(Feature)
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        for name, w in self.form_builder.widgets.items():
            form_layout.addRow(name, w)
            if name == "grants":
                self.grants = w  # type: ignore[assignment]
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(form_container)
        splitter.addWidget(scroll)

        # right catalog
        tabs = QTabWidget()
        kinds = [
            "feature",
            "class",
            "subclass",
            "item",
            "spellcasting",
            "spell",
            "race",
            "background",
        ]
        for kind in kinds:
            list_widget = CatalogList()
            for obj in DAO().load_by_kind(kind):
                rec = Record(uuid=obj.id, kind=obj.kind, name=obj.name)
                list_widget.add_record(rec)
            tabs.addTab(list_widget, kind.title())
        splitter.addWidget(tabs)

        # footer
        footer = QHBoxLayout()
        self.error_label = QLabel()
        footer.addWidget(self.error_label)
        footer.addStretch(1)
        submit = QPushButton("Submit")
        submit.setProperty("class", "primary")
        submit.clicked.connect(self.on_submit)
        footer.addWidget(submit)
        root.addLayout(footer)

    # handlers -------------------------------------------------------
    def on_submit(self) -> None:
        try:
            payload = self.form_builder.get_payload()
            payload["kind"] = "feature"
            payload["grants"] = self.grants.uuids()  # type: ignore[attr-defined]
            feature = Feature(**payload)
            DAO().save(feature)
            self.error_label.setText("saved")
            self.app.pop()
        except ValidationErrorUI as e:
            self.form_builder.set_errors(e.errors)
            self.error_label.setText("invalid")
        except Exception as ex:  # pragma: no cover - unexpected
            self.error_label.setText(str(ex))
