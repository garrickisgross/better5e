"""LiveCharacter model for Better5e.

This provides a hydrated, mutable representation of a :class:`Character` that
can be sent to a frontend.  It merges all granted game objects, resolves
modifiers, and exposes helper methods for common lookups.
"""

from __future__ import annotations

from collections import deque
from typing import Any
from uuid import UUID

from pydantic import ConfigDict, Field

from character import Character
from dao import GameObjectDAO
from modifiers import ModifierOperation
from game_objects import GameObject


class LiveCharacter(Character):
    """A live, dynamic version of a character."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dao: GameObjectDAO | None = Field(default=None, exclude=True)
    events: list[str] = Field(default_factory=list)

    def __init__(self, character: Character, dao: GameObjectDAO):
        # copy base character data and hydrate grants
        super().__init__(**character.model_dump())
        object.__setattr__(self, "dao", dao)
        self.apply_grants(dao)

    # ------------------------------------------------------------------
    # Mutation helpers
    def grant(self, obj_id: UUID) -> None:
        """Grant a new object to the character and apply its grants."""
        obj = self.dao.load(obj_id)
        self._apply_grants_from(obj)
        self.events.append(f"granted:{obj_id}")

    def _apply_grants_from(self, obj: GameObject) -> None:
        queue = deque([obj])
        seen: set[UUID] = {o.uuid for o in self.all_game_objects()}
        while queue:
            current = queue.popleft()
            if current.uuid in seen:
                continue
            seen.add(current.uuid)
            self.add_game_object(current)
            for grant_id in current.grants:
                granted = self.dao.load(grant_id)
                queue.append(granted)

    def set_data(self, path: str, value: Any) -> None:
        """Set a value using a dotted path (e.g. ``"stats.strength"``)."""
        parts = path.split(".")
        target: Any = self
        for part in parts[:-1]:
            target = target[part] if isinstance(target, dict) else getattr(target, part)
        last = parts[-1]
        if isinstance(target, dict):
            target[last] = value
        else:
            setattr(target, last, value)
        self.events.append(f"set:{path}")

    # ------------------------------------------------------------------
    # Derived/computed helpers
    def get_stat(self, key: str) -> int:
        """Return a stat value after applying modifiers."""
        value = self.stats.get(key, 0)
        for mod in self.all_modifiers():
            if mod.target == f"stats.{key}" and mod.operation != ModifierOperation.GRANT:
                value = mod.apply(value)
        return value

    def get_modifier(self, key: str) -> int:
        """Return the modifier for a given stat."""
        return (self.get_stat(key) - 10) // 2

    def to_dict(self) -> dict[str, Any]:
        """Serialize the live character for the frontend."""
        return self.model_dump()
