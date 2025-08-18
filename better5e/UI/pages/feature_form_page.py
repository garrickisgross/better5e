from __future__ import annotations

import json

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QComboBox,
)
from PyQt6.QtGui import QDrag

from pydantic import ValidationError

from better5e.UI.core.basepage import BasePage
from better5e.UI.core.style.theme import add_shadow
from better5e.UI.components.schema_form_builder import SchemaFormBuilder
from better5e.UI.components.actions_editor import ActionsEditor
from better5e.UI.components.modifiers_editor import ModifiersEditor
from better5e.UI.components.drop_zone import DropZone
from better5e.dao.sqlite import DAO
from better5e.models.game_object import Feature
from better5e.models.enums import RechargeType


class FeatureFormPage(BasePage):
    """Form for creating or editing a Feature."""

    def __init__(self, app) -> None:
        super().__init__(app, "Feature")
        add_shadow(self)

        body = self.layout()

        # header ---------------------------------------------------------------
        header = QHBoxLayout()
        back = QPushButton("Back")
        back.clicked.connect(self.app.pop)
        header.addWidget(back)
        header.addStretch(1)
        body.addLayout(header)

        # tabs -----------------------------------------------------------------
        tabs = QTabWidget()
        body.addWidget(tabs)
        add_shadow(tabs)

        # Info tab -------------------------------------------------------------
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        self.form_builder = SchemaFormBuilder()
        schema = {
            "name": (QLineEdit, {}),
            "desc": (QTextEdit, {}),
            "uses_max": (QSpinBox, {"min": 0}),
            "recharge": (QComboBox, {"enum": list(RechargeType)}),
        }
        form_widget = self.form_builder.build(schema)
        info_layout.addWidget(form_widget)
        info_layout.addStretch(1)
        tabs.addTab(info_tab, "Info")

        # references to fields
        self.name_edit: QLineEdit = self.form_builder.fields["name"]  # type: ignore
        self.desc_edit: QTextEdit = self.form_builder.fields["desc"]  # type: ignore
        self.uses_edit: QSpinBox = self.form_builder.fields["uses_max"]  # type: ignore
        self.recharge_combo: QComboBox = self.form_builder.fields["recharge"]  # type: ignore
        self.recharge_combo.setEnabled(False)

        self.name_edit.textChanged.connect(self._validate)
        self.desc_edit.textChanged.connect(self._validate)
        self.uses_edit.valueChanged.connect(self._on_uses_changed)
        self.recharge_combo.currentIndexChanged.connect(self._validate)

        # Actions tab ----------------------------------------------------------
        self.actions_editor = ActionsEditor()
        tabs.addTab(self.actions_editor, "Actions")

        # Modifiers tab --------------------------------------------------------
        self.mod_editor = ModifiersEditor()
        tabs.addTab(self.mod_editor, "Modifiers")

        # Grants tab -----------------------------------------------------------
        grants_tab = QWidget()
        grants_layout = QHBoxLayout(grants_tab)
        self.drop_zone = DropZone()
        left = QVBoxLayout()
        left.addWidget(QLabel("Grants"))
        left.addWidget(self.drop_zone)
        left.addStretch(1)
        grants_layout.addLayout(left)

        catalog = QWidget()
        cat_layout = QVBoxLayout(catalog)
        dao = DAO()
        for kind in ["feature", "item", "spell", "proficiency"]:
            items = dao.load_by_kind(kind)
            if not items:
                continue
            cat_layout.addWidget(QLabel(kind.title()))
            for obj in items:
                btn = QLabel(obj.name)
                btn.setProperty("kind", kind)
                btn.setProperty("id", str(obj.id))
                btn.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
                btn.setStyleSheet("padding:2px;border:1px solid #888;")
                btn.mousePressEvent = lambda e, o=obj: self._start_drag(e, o)
                cat_layout.addWidget(btn)
        cat_layout.addStretch(1)
        grants_layout.addWidget(catalog)
        tabs.addTab(grants_tab, "Grants")

        # footer ---------------------------------------------------------------
        footer = QHBoxLayout()
        footer.addStretch(1)
        self.error_label = QLabel()
        footer.addWidget(self.error_label)
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setProperty("class", "primary")
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(self._on_submit)
        footer.addWidget(self.submit_btn)
        body.addLayout(footer)

    # ------------------------------------------------------------------ utils
    def _start_drag(self, event, obj) -> None:  # pragma: no cover - drag is hard to test
        mime = json.dumps({"kind": obj.kind, "id": str(obj.id), "name": obj.name})
        md = Qt.QMimeData()
        md.setText(mime)
        drag = QDrag(self)
        drag.setMimeData(md)
        drag.exec()

    def _on_uses_changed(self, value: int) -> None:
        self.recharge_combo.setEnabled(value > 0)
        if value == 0:
            self.recharge_combo.setCurrentIndex(0)  # pragma: no cover
        self._validate()

    def _validate(self) -> None:
        name_ok = bool(self.name_edit.text().strip())
        desc_ok = bool(self.desc_edit.toPlainText().strip())
        uses = self.uses_edit.value()
        if uses > 0:
            recharge_ok = self.recharge_combo.currentData() is not None
        else:
            recharge_ok = True
        self.submit_btn.setEnabled(name_ok and desc_ok and recharge_ok)

    def _on_submit(self) -> None:
        data = {
            "name": self.name_edit.text().strip(),
            "desc": self.desc_edit.toPlainText().strip(),
            "actions": self.actions_editor.actions(),
            "modifiers": self.mod_editor.modifiers(),
            "grants": list(self.drop_zone.ids),
        }
        uses = self.uses_edit.value()
        if uses > 0:
            data["uses_max"] = uses
            data["recharge"] = self.recharge_combo.currentData()
        try:
            feature = Feature(**data)
        except ValidationError as e:  # pragma: no cover
            self.error_label.setText(str(e))
            return
        DAO().save(feature)
        self.error_label.setText("Feature saved")
        self.app.pop()
