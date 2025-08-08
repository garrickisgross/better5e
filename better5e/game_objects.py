from __future__ import annotations

"""Core game object models."""

from typing import Any, Dict, List, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .modifiers import Modifier


class GameObject(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    modifiers: List[Modifier] = Field(default_factory=list)
    grants: List[UUID] = Field(default_factory=list)


class Feature(GameObject):
    type: Literal["feature"] = "feature"


class Item(GameObject):
    type: Literal["item"] = "item"


class Spell(GameObject):
    type: Literal["spell"] = "spell"


class Race(GameObject):
    type: Literal["race"] = "race"


class Background(GameObject):
    type: Literal["background"] = "background"


class CharacterClass(GameObject):
    type: Literal["class"] = "class"
