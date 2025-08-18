from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QSplitter,
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

        self.form_builder = SchemaFormBuilder(Feature)
        self.grants = self.form_builder.widgets_for("grants")  # type: ignore[assignment]
        self.grants.accept_kinds = [
            "feature",
            "class",
            "subclass",
            "item",
            "spellcasting",
            "spell",
            "race",
            "background",
        ]

        self.tabs = QTabWidget()
        splitter.addWidget(self.tabs)

        info = QWidget()
        info_form = QFormLayout(info)
        for field in ["name", "desc"]:
            info_form.addRow(
                self.form_builder.label_for(field),
                self.form_builder.widgets_for(field),
            )
        self.tabs.addTab(info, "Info")

        actions_tab = QWidget()
        actions_form = QFormLayout(actions_tab)
        actions_form.addRow(
            self.form_builder.label_for("actions"),
            self.form_builder.widgets_for("actions"),
        )
        actions_form.addRow(
            self.form_builder.label_for("uses_max"),
            self.form_builder.widgets_for("uses_max"),
        )
        actions_form.addRow(
            self.form_builder.label_for("recharge"),
            self.form_builder.widgets_for("recharge"),
        )
        self.tabs.addTab(actions_tab, "Actions & Uses")

        mod_tab = QWidget()
        mod_layout = QVBoxLayout(mod_tab)
        mod_layout.addWidget(QLabel("Coming soon"))
        self.tabs.addTab(mod_tab, "Modifier")

        grants_tab = QWidget()
        grants_layout = QVBoxLayout(grants_tab)
        grants_layout.addWidget(self.grants)
        self.tabs.addTab(grants_tab, "Grants")
        self._grants_index = self.tabs.indexOf(grants_tab)

        self.catalog_tabs = QTabWidget()
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
            self.catalog_tabs.addTab(list_widget, kind.title())
        splitter.addWidget(self.catalog_tabs)
        self.catalog_tabs.hide()

        self.tabs.currentChanged.connect(self._on_tab_change)
        self._on_tab_change(self.tabs.currentIndex())

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

    def _on_tab_change(self, idx: int) -> None:
        self.catalog_tabs.setVisible(idx == self._grants_index)
