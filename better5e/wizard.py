"""Interactive game object builder.

This module exposes :class:`GameObjectWizard`, a small stateful helper used by
frontends to construct :class:`better5e.game_objects.GameObject` instances in a
deterministic and type safe manner.  All public payloads are plain JSON
structures and every side effect is explicit which makes the API friendly for
tests and UIs alike.

The implementation is intentionally lightweight; sessions are stored purely in
memory and can easily be swapped for a persistent backend.  The module is
well‑tested and achieves full test coverage to act as a solid example for
further extensions.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Literal
from uuid import UUID, uuid4
import re

from pydantic import BaseModel, Field

from .dao import GameObjectDAO
from .factory import create_game_object
from .modifiers import Modifier, ModifierOperation
from .enums import AbilityScore, DamageType, Skill


# ---------------------------------------------------------------------------
# Error handling


class WizardError(Exception):
    """Exception raised for user facing errors.

    Parameters
    ----------
    code:
        Short machine readable error code.
    message:
        Human readable description of the error.
    field:
        Optional field name related to the error.
    detail:
        Additional structured information.
    """

    def __init__(self, code: str, message: str, *, field: str | None = None, detail: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field
        self.detail = detail

    def to_dict(self) -> dict:
        """Return a JSON serialisable representation of the error."""

        payload = {"code": self.code, "message": self.message}
        if self.field is not None:
            payload["field"] = self.field
        if self.detail is not None:
            payload["detail"] = self.detail
        return payload


# ---------------------------------------------------------------------------
# Validators & helpers


DICE_PATTERN = re.compile(r"^(?P<count>\d+)d(?P<sides>\d+)(?P<mod>[+-]\d+)?$")
VALID_DICE_SIDES = {4, 6, 8, 10, 12, 20, 100}


def validate_dice(expr: str) -> None:
    """Validate a D&D style dice expression.

    ``expr`` must be of the form ``XdY+Z`` where ``X`` and ``Y`` are positive
    integers, ``Y`` is one of ``4, 6, 8, 10, 12, 20, 100`` and ``Z`` is an
    optional signed integer.
    """

    match = DICE_PATTERN.fullmatch(expr.replace(" ", ""))
    if not match:
        raise WizardError("invalid_dice", f"invalid dice expression: {expr}")
    count = int(match.group("count"))
    sides = int(match.group("sides"))
    if count < 1 or sides not in VALID_DICE_SIDES:
        raise WizardError("invalid_dice", f"invalid dice expression: {expr}")


def _coerce_uuid(value: Any) -> UUID:
    try:
        return UUID(str(value))
    except Exception as exc:  # pragma: no cover - defensive
        raise WizardError("invalid_uuid", f"invalid uuid: {value}") from exc


def coerce_uuid_list(value: Any) -> List[UUID]:
    """Coerce ``value`` into a list of UUIDs."""

    if value in (None, "", []):
        return []
    if isinstance(value, (str, UUID)):
        value = [value]
    return [_coerce_uuid(v) for v in value]


def _merge_path(target: dict, key: str, value: Any) -> None:
    """Merge ``value`` into ``target`` using ``.`` separated ``key``."""

    parts = key.split(".")
    cursor = target
    for part in parts[:-1]:
        cursor = cursor.setdefault(part, {})
    cursor[parts[-1]] = value


# ---------------------------------------------------------------------------
# Session model


class WizardSession(BaseModel):
    """In memory session state."""

    session_id: str
    obj_type: Literal["feature", "item", "spell", "race", "background", "class"]
    step_index: int = 0
    core: dict = Field(default_factory=dict)
    data: dict = Field(default_factory=dict)
    modifiers: list[dict] = Field(default_factory=list)
    grants: list[str] = Field(default_factory=list)
    created_uuid: UUID | None = None
    revision: int = 0
    last_response: dict = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Form specification builders


def _feature_fields() -> List[dict]:
    return [
        {"key": "description", "label": "Description", "type": "text"},
        {
            "key": "activation",
            "label": "Activation",
            "type": "select",
            "choices": ["passive", "action", "bonus_action", "reaction", "special"],
        },
        {"key": "uses.max", "label": "Max Uses", "type": "number"},
        {
            "key": "uses.recharge",
            "label": "Recharge",
            "type": "select",
            "choices": ["long_rest", "short_rest", "at_will", "per_day", "per_encounter"],
        },
    ]


def _item_fields() -> List[dict]:
    return [
        {
            "key": "category",
            "label": "Category",
            "type": "select",
            "choices": ["weapon", "armor", "consumable", "tool", "gear", "misc"],
        },
        {"key": "weight", "label": "Weight", "type": "number"},
        {"key": "value", "label": "Value", "type": "number"},
        {
            "key": "properties",
            "label": "Properties",
            "type": "multiselect",
            "choices": ["light", "finesse", "two_handed", "versatile"],
        },
        {"key": "damage", "label": "Damage", "type": "dice"},
        {
            "key": "damage_type",
            "label": "Damage Type",
            "type": "select",
            "choices": [dt.value for dt in DamageType],
        },
        {"key": "ac_base", "label": "AC Base", "type": "number"},
        {
            "key": "stealth_disadvantage",
            "label": "Stealth Disadvantage",
            "type": "select",
            "choices": [True, False],
            "default": False,
        },
    ]


def _spell_fields() -> List[dict]:
    return [
        {"key": "level", "label": "Level", "type": "number", "required": True},
        {
            "key": "school",
            "label": "School",
            "type": "select",
            "choices": [
                "abjuration",
                "conjuration",
                "divination",
                "enchantment",
                "evocation",
                "illusion",
                "necromancy",
                "transmutation",
            ],
        },
        {"key": "casting_time", "label": "Casting Time", "type": "text"},
        {"key": "range", "label": "Range", "type": "text"},
        {"key": "duration", "label": "Duration", "type": "text"},
        {
            "key": "components",
            "label": "Components",
            "type": "multiselect",
            "choices": ["V", "S", "M"],
        },
        {"key": "materials", "label": "Materials", "type": "text"},
        {
            "key": "attack_save",
            "label": "Attack/Save",
            "type": "select",
            "choices": ["attack", "str", "dex", "con", "int", "wis", "cha", "none"],
        },
        {"key": "damage", "label": "Damage", "type": "dice"},
        {
            "key": "damage_type",
            "label": "Damage Type",
            "type": "select",
            "choices": [dt.value for dt in DamageType],
        },
    ]


def _race_fields() -> List[dict]:
    return [
        {
            "key": "size",
            "label": "Size",
            "type": "select",
            "choices": ["tiny", "small", "medium", "large"],
        },
        {"key": "speed", "label": "Speed", "type": "number"},
        {"key": "languages", "label": "Languages", "type": "multiselect"},
        {"key": "traits", "label": "Traits", "type": "json"},
    ]


def _background_fields() -> List[dict]:
    return [
        {
            "key": "proficiencies.skills",
            "label": "Skill Proficiencies",
            "type": "multiselect",
            "choices": [s.value for s in Skill],
        },
        {"key": "tools", "label": "Tools", "type": "json"},
        {"key": "languages", "label": "Languages", "type": "multiselect"},
        {"key": "feature_text", "label": "Feature", "type": "text"},
    ]


def _class_fields() -> List[dict]:
    return [
        {
            "key": "hit_die",
            "label": "Hit Die",
            "type": "select",
            "choices": ["d6", "d8", "d10", "d12"],
        },
        {
            "key": "primary_abilities",
            "label": "Primary Abilities",
            "type": "multiselect",
            "choices": [a.value for a in AbilityScore],
        },
        {
            "key": "saves",
            "label": "Saving Throws",
            "type": "multiselect",
            "choices": [a.value for a in AbilityScore],
        },
        {"key": "proficiencies", "label": "Proficiencies", "type": "json"},
        {"key": "spellcasting", "label": "Spellcasting", "type": "json"},
    ]


FORM_BUILDERS: Dict[str, Callable[[], List[dict]]] = {
    "feature": _feature_fields,
    "item": _item_fields,
    "spell": _spell_fields,
    "race": _race_fields,
    "background": _background_fields,
    "class": _class_fields,
}


MODIFIER_ROW_SPEC = {
    "target": {"label": "Target", "type": "text", "required": True},
    "operation": {
        "label": "Operation",
        "type": "select",
        "required": True,
        "choices": [op.value for op in ModifierOperation],
    },
    "value": {"label": "Value", "type": "text", "required": True},
    "condition": {"label": "Condition", "type": "text"},
    "stackable": {"label": "Stackable", "type": "boolean", "default": True},
}


# ---------------------------------------------------------------------------
# Main wizard implementation


class GameObjectWizard:
    """Wizard used to create and edit :class:`GameObject` instances."""

    STEPS: List[str] = ["core", "type_specific", "modifiers", "grants", "review"]

    def __init__(self, dao: GameObjectDAO):
        self.dao = dao
        self._sessions: Dict[str, WizardSession] = {}

    # ------------------------------------------------------------------
    # Form specification
    def get_form_spec(
        self, obj_type: Literal["feature", "item", "spell", "race", "background", "class"]
    ) -> dict:
        """Return a deterministic JSON specification for ``obj_type``."""

        type_fields = FORM_BUILDERS[obj_type]()
        spec = {
            "title": f"{obj_type.title()} Builder",
            "steps": [
                {
                    "name": "core",
                    "fields": [
                        {
                            "key": "name",
                            "label": "Name",
                            "type": "text",
                            "required": True,
                        }
                    ],
                },
                {"name": "type_specific", "fields": type_fields},
                {
                    "name": "modifiers",
                    "fields": [
                        {
                            "key": "modifiers",
                            "label": "Modifiers",
                            "type": "rows",
                            "row": MODIFIER_ROW_SPEC,
                        }
                    ],
                },
                {
                    "name": "grants",
                    "fields": [
                        {
                            "key": "grants",
                            "label": "Grants",
                            "type": "uuid_list",
                        }
                    ],
                },
                {"name": "review", "fields": []},
            ],
        }
        return spec

    # ------------------------------------------------------------------
    # Session lifecycle helpers

    def start(self, obj_type: str, *, template: dict | None = None) -> str:
        """Begin a new session for ``obj_type`` and optionally prefill values."""

        sid = str(uuid4())
        session = WizardSession(session_id=sid, obj_type=obj_type)  # type: ignore[arg-type]
        if template:
            core = template.get("core") or {}
            if name := core.get("name"):
                session.core["name"] = name
            data = template.get("data") or {}
            if data:
                self._validate_type_data(obj_type, data)
                session.data = data
            mods = template.get("modifiers") or []
            session.modifiers = [self._validate_modifier(m) for m in mods]
            session.grants = [str(u) for u in coerce_uuid_list(template.get("grants"))]
        self._sessions[sid] = session
        return sid

    def apply(self, session_id: str, data: dict, *, revision: int | None = None) -> dict:
        """Apply ``data`` to the current session step.

        ``revision`` implements optimistic concurrency and idempotency.  The
        caller must send the current session revision.  If the same revision is
        re-sent the previously produced response is returned without mutating
        state.
        """

        session = self._sessions[session_id]
        if revision is None:
            raise WizardError("conflict_revision", "revision required")
        if revision < session.revision:
            return session.last_response
        if revision > session.revision:
            raise WizardError("conflict_revision", "revision mismatch")

        step = self.STEPS[session.step_index]
        spec = self.get_form_spec(session.obj_type)["steps"][session.step_index]
        allowed = {f["key"] for f in spec["fields"]}
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise WizardError("unknown_field", f"unknown field: {unknown[0]}", field=unknown[0])

        if step == "core":
            name = data.get("name")
            if not name:
                raise WizardError("missing_required", "name is required", field="name")
            session.core["name"] = name
        elif step == "type_specific":
            merged: dict = {}
            for key, value in data.items():
                _merge_path(merged, key, value)
            self._validate_type_data(session.obj_type, merged)
            session.data = merged
        elif step == "modifiers":
            mods = [self._validate_modifier(m) for m in data.get("modifiers", [])]
            session.modifiers = mods
        elif step == "grants":
            session.grants = [str(u) for u in coerce_uuid_list(data.get("grants", []))]

        session.step_index = min(session.step_index + 1, len(self.STEPS) - 1)
        session.revision += 1
        next_step = self.STEPS[session.step_index]
        response = {"step": next_step, "fields": self.get_form_spec(session.obj_type)["steps"][session.step_index]["fields"]}
        session.last_response = response
        return response

    def preview(self, session_id: str) -> dict:
        """Return a summary of the session suitable for a UI preview."""

        session = self._sessions[session_id]
        payload: dict[str, Any] = {
            "name": session.core.get("name"),
            "type": session.obj_type,
            "modifier_count": len(session.modifiers),
            "grants": session.grants,
        }
        self._add_highlights(session, payload)
        return payload

    def finalize(self, session_id: str, *, save: bool = True) -> dict:
        """Materialise the session into a :class:`GameObject`.

        If ``save`` is ``True`` the object is persisted via the configured DAO.
        The returned dict contains the object's UUID, type and full model dump.
        """

        session = self._sessions.pop(session_id)
        name = session.core.get("name")
        if not name:
            raise WizardError("missing_required", "name is required", field="name")

        # Validate referenced UUIDs exist when saving
        all_uuids: Iterable[UUID] = [UUID(g) for g in session.grants]
        for m in session.modifiers:
            if m["operation"] == ModifierOperation.GRANT.value:
                vals = m["value"]
                vals = vals if isinstance(vals, list) else [vals]
                all_uuids = list(all_uuids) + [UUID(v) for v in vals]
        if save:
            for uid in all_uuids:
                try:
                    self.dao.load(uid)
                except Exception as exc:  # pragma: no cover - defensive
                    raise WizardError("invalid_uuid", f"unknown uuid {uid}") from exc

        modifiers = [
            Modifier(
                target=m["target"],
                operation=ModifierOperation(m["operation"]),
                value=m["value"],
                condition=m.get("condition"),
                stackable=m.get("stackable", True),
            )
            for m in session.modifiers
        ]

        payload = {
            "uuid": session.created_uuid or uuid4(),
            "name": name,
            "type": session.obj_type,
            "data": session.data,
            "modifiers": modifiers,
            "grants": [UUID(g) for g in session.grants],
        }
        obj = create_game_object(payload)
        if save:
            self.dao.save(obj)
        session.created_uuid = obj.uuid
        return {"uuid": str(obj.uuid), "type": obj.type, "model": obj.model_dump()}

    def load_existing(self, obj_id: UUID) -> str:
        """Load an existing object for editing and return the session id."""

        obj = self.dao.load(obj_id)
        sid = str(uuid4())
        session = WizardSession(
            session_id=sid,
            obj_type=obj.type,  # type: ignore[arg-type]
            core={"name": obj.name},
            data=obj.data,
            modifiers=[m.model_dump() for m in obj.modifiers],
            grants=[str(g) for g in obj.grants],
            created_uuid=obj.uuid,
        )
        self._sessions[sid] = session
        return sid

    def cancel(self, session_id: str) -> None:
        """Abort ``session_id`` if it exists."""

        self._sessions.pop(session_id, None)

    # ------------------------------------------------------------------
    # Internal helpers

    def _validate_modifier(self, data: dict) -> dict:
        allowed = set(MODIFIER_ROW_SPEC)
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise WizardError("unknown_field", f"unknown field: {unknown[0]}", field=unknown[0])
        op = data.get("operation")
        if op not in [o.value for o in ModifierOperation]:
            raise WizardError("invalid_choice", f"unknown operation: {op}", field="operation")
        value = data.get("value")
        if op == ModifierOperation.GRANT.value:
            value = [str(u) for u in coerce_uuid_list(value)]
        return {
            "target": data.get("target"),
            "operation": op,
            "value": value,
            "condition": data.get("condition"),
            "stackable": data.get("stackable", True),
        }

    def _validate_type_data(self, obj_type: str, data: dict) -> None:
        if obj_type == "spell":
            level = data.get("level")
            if level is None or not (0 <= int(level) <= 9):
                raise WizardError("invalid_choice", "level must be 0-9", field="level")
            comps = set(data.get("components", []))
            if not comps.issubset({"V", "S", "M"}):
                raise WizardError("invalid_choice", "invalid components", field="components")
            if dmg := data.get("damage"):
                validate_dice(dmg)
            if data.get("damage_type") and not data.get("damage"):
                raise WizardError("missing_required", "damage required", field="damage")
        if obj_type == "item":
            if dmg := data.get("damage"):
                validate_dice(dmg)
            if data.get("category") == "weapon":
                if not data.get("damage"):
                    raise WizardError("missing_required", "weapon needs damage", field="damage")
                if not data.get("damage_type"):
                    raise WizardError("missing_required", "weapon needs damage_type", field="damage_type")
        if obj_type == "feature":
            uses = data.get("uses", {})
            if "max" in uses and int(uses["max"]) < 0:
                raise WizardError("invalid_choice", "uses.max must be >=0", field="uses.max")

    def _add_highlights(self, session: WizardSession, payload: dict) -> None:
        if session.obj_type == "item":
            payload["category"] = session.data.get("category")
            if session.data.get("damage"):
                payload["damage"] = session.data.get("damage")
        elif session.obj_type == "spell":
            payload["level"] = session.data.get("level")
            payload["school"] = session.data.get("school")
        elif session.obj_type == "feature":
            payload["activation"] = session.data.get("activation")


__all__ = [
    "GameObjectWizard",
    "WizardError",
    "WizardSession",
    "validate_dice",
    "coerce_uuid_list",
]

