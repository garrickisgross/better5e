from __future__ import annotations

import types
from enum import Enum
from typing import Any, Union, get_args, get_origin
from uuid import UUID

from PyQt6.QtWidgets import QComboBox, QLineEdit, QSpinBox, QTextEdit, QWidget

from better5e.models.game_object import Action, Modifier
from better5e.UI.components.grant_picker import GrantPicker
from better5e.UI.components.list_editor import ListEditor


class SchemaFormBuilder:
    """Builds Qt widgets from Pydantic field annotations."""

    def __init__(self, hints: dict[str, dict[str, Any]] | None = None) -> None:
        self.hints = hints or {}

    # ------------------------------------------------------------------
    def build_widget(self, name: str, annotation: Any) -> QWidget:
        """Return an appropriate widget for *annotation*.

        The mapping is intentionally small but covers the field types required by
        the Feature model used in tests.
        """

        hint = self.hints.get(name, {})

        # Strings --------------------------------------------------------
        if annotation is str:
            if hint.get("multiline") or name == "desc":
                return QTextEdit()
            return QLineEdit()

        # Optional integers ---------------------------------------------
        if self._is_optional(annotation, int):
            spin = QSpinBox()
            spin.setMinimum(-10_000)
            spin.setMaximum(10_000)
            spin.setSpecialValueText("")  # Allows representing None
            return spin

        # Enumerations ---------------------------------------------------
        enum_cls = self._enum_for(annotation)
        if enum_cls is not None:
            combo = QComboBox()
            combo.addItem("")  # blank choice for None
            for member in enum_cls:
                combo.addItem(member.value)
            return combo

        # Lists ----------------------------------------------------------
        if self._is_list_of(annotation, Action):
            return ListEditor(Action)
        if self._is_list_of(annotation, Modifier):
            return ListEditor(Modifier)
        if self._is_list_of(annotation, UUID):
            return GrantPicker()

        # Fallback
        return QLineEdit()

    # ------------------------------------------------------------------
    def _is_optional(self, ann: Any, inner: type[Any]) -> bool:
        origin = get_origin(ann)
        if origin in (Union, types.UnionType):
            args = [a for a in get_args(ann) if a is not type(None)]
            return len(args) == 1 and args[0] is inner
        return False

    # ------------------------------------------------------------------
    def _enum_for(self, ann: Any) -> type[Enum] | None:
        if isinstance(ann, type) and issubclass(ann, Enum):
            return ann
        origin = get_origin(ann)
        if origin in (Union, types.UnionType):
            for arg in get_args(ann):
                if isinstance(arg, type) and issubclass(arg, Enum):
                    return arg
        return None

    # ------------------------------------------------------------------
    def _is_list_of(self, ann: Any, inner: type[Any]) -> bool:
        origin = get_origin(ann)
        return origin is list and get_args(ann)[0] is inner
