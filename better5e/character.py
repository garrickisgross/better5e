from __future__ import annotations

"""Character model for Better5e."""

from collections import deque
from typing import Dict, Iterable, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from enums import AbilityScore
from game_objects import (
    Background,
    CharacterClass,
    Feature,
    GameObject,
    Item,
    Race,
    Spell,
)
from modifiers import Modifier, ModifierOperation


class Character(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str
    race: Optional[Race] = None
    background: Optional[Background] = None
    classes: Dict[UUID, int] = Field(default_factory=dict)  # class id -> level
    features: List[Feature] = Field(default_factory=list)
    items: List[Item] = Field(default_factory=list)
    spells: List[Spell] = Field(default_factory=list)
    stats: Dict[str, int] = Field(
        default_factory=lambda: {a.value: 10 for a in AbilityScore}
    )

    def all_game_objects(self) -> List[GameObject]:
        objs: List[GameObject] = []
        if self.race:
            objs.append(self.race)
        if self.background:
            objs.append(self.background)
        objs.extend(self.features)
        objs.extend(self.items)
        objs.extend(self.spells)
        # classes not stored as GameObjects but may be loaded via DAO
        return objs

    def all_modifiers(self) -> Iterable[Modifier]:
        for obj in self.all_game_objects():
            yield from obj.modifiers

    def get_stat(self, key: str) -> int:
        value = self.stats.get(key, 0)
        for mod in self.all_modifiers():
            if mod.target == f"stats.{key}" and mod.operation != ModifierOperation.GRANT:
                value = mod.apply(value)
        return value

    def add_game_object(self, obj: GameObject) -> None:
        if isinstance(obj, Feature):
            self.features.append(obj)
        elif isinstance(obj, Item):
            self.items.append(obj)
        elif isinstance(obj, Spell):
            self.spells.append(obj)
        elif isinstance(obj, Race):
            self.race = obj
        elif isinstance(obj, Background):
            self.background = obj
        elif isinstance(obj, CharacterClass):
            self.classes[obj.uuid] = self.classes.get(obj.uuid, 0) + 1
        else:
            raise TypeError(f"Unsupported game object: {obj}")

    def apply_grants(self, dao: "GameObjectDAO") -> None:  # type: ignore[quote]
        queue = deque(self.all_game_objects())
        seen: set[UUID] = set()
        while queue:
            obj = queue.popleft()
            for grant_id in obj.grants:
                if grant_id in seen:
                    continue
                granted = dao.load(grant_id)
                self.add_game_object(granted)
                queue.append(granted)
                seen.add(grant_id)
