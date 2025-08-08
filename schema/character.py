from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Any

from schema.primitives import AbilityScore, Skill


class CharacterClass(BaseModel):
    class_id: UUID
    level: int
    subclass_id: Optional[UUID] = None


class Character(BaseModel):
    ac: int
    ability_scores: dict[str, AbilityScore]
    proficiency_bonus: int
    skills: dict[str, Skill]
    background: UUID
    features: list[UUID]
    inventory: list[UUID]
    classes: list[CharacterClass]
    spellcasting: Optional[dict[Any, Any]]  # change when we work on spellcasting object

    @property
    def level(self) -> int:
        return sum(c.level for c in self.classes)

