from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from schema.primitives import AbilityScore, Skill
from schema.spellcasting import Spellcasting


class CharacterClass(BaseModel):
    class_id: UUID
    level: int
    subclass_id: Optional[UUID] = None


class Character(BaseModel):
    ac: int
    ability_scores: dict[str, AbilityScore]
    proficiency_bonus: int
    skills: dict[str, Skill]
    features: list[UUID]
    inventory: list[UUID]
    classes: list[CharacterClass]
    spellcasting: dict[str, Spellcasting] = Field(default_factory=dict)

    @property
    def level(self) -> int:
        return sum(c.level for c in self.classes)

