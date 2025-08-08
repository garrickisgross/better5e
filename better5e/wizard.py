from __future__ import annotations

"""Type-aware wizard for constructing :class:`GameObject` instances.

The wizard exposes a step-based API suitable for driving a dynamic frontend.
It keeps all state in memory using simple dataclasses so it can be easily
swapped for a persistent implementation later.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal
from uuid import UUID, uuid4
import re

from .dao import GameObjectDAO
from .factory import create_game_object
from .modifiers import Modifier, ModifierOperation
from .enums import DamageType, AbilityScore, Skill


# ----------------------------------------------------------------------
# Field specifications -------------------------------------------------

TYPE_FIELDS: Dict[str, List[dict[str, Any]]] = {
    "feature": [
        {"key": "data.description", "label": "Description", "type": "text"},
        {
            "key": "data.activation",
            "label": "Activation",
            "type": "select",
            "choices": [
                "passive",
                "action",
                "bonus_action",
                "reaction",
                "special",
            ],
        },
        {"key": "data.uses.max", "label": "Max Uses", "type": "number"},
        {
            "key": "data.uses.recharge",
            "label": "Recharge",
            "type": "select",
            "choices": [
                "long_rest",
                "short_rest",
                "at_will",
                "per_day",
                "per_encounter",
            ],
        },
    ],
    "item": [
        {
            "key": "data.category",
            "label": "Category",
            "type": "select",
            "choices": [
                "weapon",
                "armor",
                "consumable",
                "tool",
                "gear",
                "misc",
            ],
        },
        {"key": "data.weight", "label": "Weight", "type": "number"},
        {"key": "data.value", "label": "Value", "type": "number"},
        {
            "key": "data.properties",
            "label": "Properties",
            "type": "multiselect",
            "choices": ["light", "finesse", "two_handed", "versatile"],
        },
        {"key": "data.damage", "label": "Damage", "type": "dice"},
        {
            "key": "data.damage_type",
            "label": "Damage Type",
            "type": "select",
            "choices": [dt.value for dt in DamageType],
        },
        {"key": "data.ac_base", "label": "AC Base", "type": "number"},
        {
            "key": "data.stealth_disadvantage",
            "label": "Stealth Disadvantage",
            "type": "select",
            "choices": [True, False],
            "default": False,
        },
    ],
    "spell": [
        {"key": "data.level", "label": "Level", "type": "number", "required": True},
        {
            "key": "data.school",
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
        {"key": "data.casting_time", "label": "Casting Time", "type": "text"},
        {"key": "data.range", "label": "Range", "type": "text"},
        {"key": "data.duration", "label": "Duration", "type": "text"},
        {
            "key": "data.components",
            "label": "Components",
            "type": "multiselect",
            "choices": ["V", "S", "M"],
        },
        {"key": "data.materials", "label": "Materials", "type": "text"},
        {
            "key": "data.attack_save",
            "label": "Attack/Save",
            "type": "select",
            "choices": [
                "attack",
                "str",
                "dex",
                "con",
                "int",
                "wis",
                "cha",
                "none",
            ],
        },
        {"key": "data.damage", "label": "Damage", "type": "dice"},
        {
            "key": "data.damage_type",
            "label": "Damage Type",
            "type": "select",
            "choices": [dt.value for dt in DamageType],
        },
    ],
    "race": [
        {
            "key": "data.size",
            "label": "Size",
            "type": "select",
            "choices": ["tiny", "small", "medium", "large"],
        },
        {"key": "data.speed", "label": "Speed", "type": "number"},
        {"key": "data.languages", "label": "Languages", "type": "multiselect"},
        {"key": "data.traits", "label": "Traits", "type": "json"},
    ],
    "background": [
        {
            "key": "data.proficiencies.skills",
            "label": "Skill Proficiencies",
            "type": "multiselect",
            "choices": [s.value for s in Skill],
        },
        {"key": "data.tools", "label": "Tools", "type": "json"},
        {"key": "data.languages", "label": "Languages", "type": "multiselect"},
        {"key": "data.feature_text", "label": "Feature", "type": "text"},
    ],
    "class": [
        {
            "key": "data.hit_die",
            "label": "Hit Die",
            "type": "select",
            "choices": ["d6", "d8", "d10", "d12"],
        },
        {
            "key": "data.primary_abilities",
            "label": "Primary Abilities",
            "type": "multiselect",
            "choices": [a.value for a in AbilityScore],
        },
        {
            "key": "data.saves",
            "label": "Saving Throws",
            "type": "multiselect",
            "choices": [a.value for a in AbilityScore],
        },
        {"key": "data.proficiencies", "label": "Proficiencies", "type": "json"},
        {"key": "data.spellcasting", "label": "Spellcasting", "type": "json"},
    ],
}


@dataclass
class WizardSession:
    """Simple in-memory session state."""

    obj_type: str
    name: str | None = None
    data: Dict[str, Any] = field(default_factory=dict)
    modifiers: List[Modifier] = field(default_factory=list)
    grants: List[UUID] = field(default_factory=list)
    step_index: int = 0


class GameObjectWizard:
    """Step-based wizard for building ``GameObject`` instances."""

    STEPS = ["core", "type_specific", "modifiers", "grants", "review"]

    def __init__(self, dao: GameObjectDAO):
        self.dao = dao
        self._sessions: Dict[str, WizardSession] = {}

    # ------------------------------------------------------------------
    # Form specification
    def get_form_spec(
        self, obj_type: Literal["feature", "item", "spell", "race", "background", "class"]
    ) -> dict:
        """Return the JSON-safe form specification for *obj_type*."""

        steps = [
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
            {
                "name": "type_specific",
                "fields": self._type_fields(obj_type),
            },
            {
                "name": "modifiers",
                "fields": [
                    {
                        "key": "modifiers",
                        "label": "Modifiers",
                        "type": "json",
                        "required": False,
                        "help": "List of modifier definitions",
                    }
                ],
            },
            {
                "name": "grants",
                "fields": [
                    {
                        "key": "grants",
                        "label": "Grants",
                        "type": "uuid",
                        "required": False,
                        "help": "List of granted object UUIDs",
                    }
                ],
            },
            {"name": "review", "fields": []},
        ]
        return {"title": f"{obj_type.title()} Builder", "steps": steps}

    # ------------------------------------------------------------------
    # Session lifecycle
    def start(self, obj_type: str, *, template: dict | None = None) -> str:
        """Create a new wizard session and return its ID."""

        sid = str(uuid4())
        session = WizardSession(obj_type=obj_type)
        if template:
            session.name = template.get("name")
            session.data = template.get("data", {})
            session.modifiers = [build_modifier(m) for m in template.get("modifiers", [])]
            session.grants = coerce_uuid_list(template.get("grants", []))
        self._sessions[sid] = session
        return sid

    def apply(self, session_id: str, data: dict) -> dict:
        """Apply *data* for the current step and return next-step spec."""

        session = self._sessions[session_id]
        step = self.STEPS[session.step_index]
        if step == "core":
            name = data.get("name")
            if not name:
                raise ValueError("name is required")
            if data.get("type") and data["type"] != session.obj_type:
                raise ValueError("type mismatch")
            session.name = name
        elif step == "type_specific":
            payload = data.get("data", {})
            self._validate_type_data(session.obj_type, payload)
            session.data = payload
        elif step == "modifiers":
            mods = [build_modifier(m) for m in data.get("modifiers", [])]
            session.modifiers = mods
        elif step == "grants":
            session.grants = coerce_uuid_list(data.get("grants", []))
        # advance step
        session.step_index = min(session.step_index + 1, len(self.STEPS) - 1)
        next_step = self.STEPS[session.step_index]
        spec = self.get_form_spec(session.obj_type)["steps"][self.STEPS.index(next_step)]
        return {"step": spec["name"], "fields": spec["fields"]}

    def preview(self, session_id: str) -> dict:
        """Return a preview payload for the session."""

        session = self._sessions[session_id]
        preview: dict[str, Any] = {
            "name": session.name,
            "type": session.obj_type,
            "modifiers": len(session.modifiers),
            "grants": [str(g) for g in session.grants],
        }
        self._add_highlights(session, preview)
        return preview

    def finalize(self, session_id: str, *, save: bool = True) -> dict:
        """Finalize and persist the built object, returning its model dump."""

        session = self._sessions.pop(session_id)
        if not session.name:
            raise ValueError("incomplete session")
        payload = {
            "name": session.name,
            "type": session.obj_type,
            "data": session.data,
            "modifiers": session.modifiers,
            "grants": session.grants,
        }
        obj = create_game_object(payload)
        if save:
            self.dao.save(obj)
        return {"uuid": str(obj.uuid), "type": obj.type, "model": obj.model_dump()}

    def cancel(self, session_id: str) -> None:
        """Abort the session."""

        self._sessions.pop(session_id, None)

    # ------------------------------------------------------------------
    # Internal helpers
    def _type_fields(self, obj_type: str) -> List[dict]:
        """Return form fields for the type-specific step."""

        return TYPE_FIELDS[obj_type]

    def _validate_type_data(self, obj_type: str, data: dict) -> None:
        """Validate type-specific data."""

        if obj_type == "spell":
            level = data.get("level")
            if level is None or not (0 <= int(level) <= 9):
                raise ValueError("spell level must be 0-9")
            if dmg := data.get("damage"):
                dice_validator(dmg)
            if data.get("damage_type") and not data.get("damage"):
                raise ValueError("damage_type requires damage")
        if obj_type == "item":
            if dmg := data.get("damage"):
                dice_validator(dmg)
        if obj_type == "feature":
            uses = data.get("uses", {})
            if "max" in uses and int(uses["max"]) < 0:
                raise ValueError("uses.max must be non-negative")

    def _add_highlights(self, session: WizardSession, payload: dict) -> None:
        """Add type-specific preview highlights."""

        data = session.data
        if session.obj_type == "item":
            payload["category"] = data.get("category")
            if data.get("damage"):
                payload["damage"] = data.get("damage")
        elif session.obj_type == "spell":
            payload["level"] = data.get("level")
            payload["school"] = data.get("school")
        elif session.obj_type == "feature":
            payload["activation"] = data.get("activation")


# ----------------------------------------------------------------------
# Helper utilities

def build_modifier(data: dict) -> Modifier:
    """Build a :class:`Modifier` from raw *data*."""

    op = ModifierOperation(data["operation"])
    value = data.get("value")
    if op == ModifierOperation.GRANT:
        value = coerce_uuid_list(value)
        if len(value) == 1:
            value = value[0]
    return Modifier(
        target=data["target"],
        operation=op,
        value=value,
        condition=data.get("condition"),
        stackable=data.get("stackable", True),
    )


def coerce_uuid_list(x: Any) -> List[UUID]:
    """Coerce *x* into a list of UUIDs."""

    if not x:
        return []
    if isinstance(x, (str, UUID)):
        x = [x]
    return [UUID(str(v)) for v in x]


def dice_validator(expr: str) -> None:
    """Validate a dice expression like ``"1d6+2"``."""

    if not re.fullmatch(r"\d+d\d+(?:[+-]\d+)?", expr.replace(" ", "")):
        raise ValueError(f"Invalid dice expression: {expr}")
