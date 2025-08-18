from __future__ import annotations

from typing import Dict, Type

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton

from better5e.UI.core.basepage import BasePage
from better5e.UI.main_screen.create_pages.fields.schema_form_builder import (
    SchemaFormBuilder,
)
from better5e.UI.main_screen.create_pages.fields.drop_zone import DropZone
from better5e.dao.sqlite import DAO
from better5e.models.game_object import Feature, Spell, Spellcasting

MODEL_MAP: Dict[str, Type] = {
    "Feature": Feature,
    "Spell": Spell,
    "Spellcasting": Spellcasting,
}


class CreatePage(BasePage):
    """Simple schema-driven create page."""

    def __init__(self, app, kind: str):
        super().__init__(app, f"Create {kind}")
        self.kind = kind
        layout = self.layout()

        header = QHBoxLayout()
        self.back_btn = QPushButton("\u2190 Back")
        self.back_btn.clicked.connect(self.app.pop)
        header.addWidget(self.back_btn)
        header.addStretch(1)
        header.addWidget(QLabel(f"Create {kind}"))
        header.addStretch(1)
        layout.addLayout(header)

        schema = self._load_schema(kind)
        if not schema:
            layout.addWidget(QLabel("Schema unavailable"))
            self.form = None
            self.relations = {}
            self.create_btn = QPushButton("Create")
            self.create_btn.setEnabled(False)
            layout.addWidget(self.create_btn)
            return

        self.relations = self._build_relations(schema)
        exclude = set(self.relations.keys())
        self.form = self._build_form(schema, exclude)
        layout.addWidget(self.form)
        for dz in self.relations.values():
            layout.addWidget(dz)

        self.create_btn = QPushButton("Create")
        self.create_btn.setEnabled(False)
        self.create_btn.clicked.connect(self._submit)
        layout.addWidget(self.create_btn)

        self.form.changed.connect(self._update_valid)
        QShortcut(QKeySequence("Escape"), self, activated=self.app.pop)
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self._submit)

    # schema -------------------------------------------------------------
    def _load_schema(self, kind: str) -> dict | None:
        model = MODEL_MAP.get(kind)
        if not model:
            return None
        return model.model_json_schema()

    def _build_form(self, schema: dict, exclude: set[str]) -> SchemaFormBuilder:
        return SchemaFormBuilder(schema, exclude=exclude)

    def _build_relations(self, schema: dict) -> dict[str, DropZone]:
        relations: dict[str, DropZone] = {}
        for name, prop in schema.get("properties", {}).items():
            if prop.get("type") == "array" and prop.get("items", {}).get("format") == "uuid":
                relations[name] = DropZone()
        return relations

    # submission ---------------------------------------------------------
    def _update_valid(self) -> None:
        if self.form:
            self.create_btn.setEnabled(self.form.is_valid())

    def _collect_payload(self) -> dict:
        payload = self.form.values() if self.form else {}
        for name, dz in self.relations.items():
            payload[name] = [str(u) for u in dz.values()]
        payload["kind"] = self.kind.lower()
        return payload

    def _submit(self) -> None:
        if not self.form or not self.form.is_valid():
            return
        model_cls = MODEL_MAP.get(self.kind)
        if not model_cls:
            return
        data = self._collect_payload()
        obj = model_cls(**data)
        DAO().save(obj)
        self.app.pop()
