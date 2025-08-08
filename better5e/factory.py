from __future__ import annotations

"""Factory utilities for constructing game objects from raw data."""

from typing import Dict, Type

from .game_objects import (
    Background,
    CharacterClass,
    Feature,
    GameObject,
    Item,
    Race,
    Spell,
)

_TYPE_MAP: Dict[str, Type[GameObject]] = {
    "feature": Feature,
    "item": Item,
    "spell": Spell,
    "race": Race,
    "background": Background,
    "class": CharacterClass,
}


def create_game_object(data: dict) -> GameObject:
    cls = _TYPE_MAP.get(data.get("type"), GameObject)
    return cls(**data)
