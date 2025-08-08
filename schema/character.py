from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from schema.primitives import AbilityScore, Skill
from schema.spellcasting import Spellcasting
from schema.rollable import Rollable


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
    race: UUID
    features: list[UUID]
    inventory: list[UUID]
    classes: list[CharacterClass]
    spellcasting: dict[str, Spellcasting] = Field(default_factory=dict)
    rollables: dict[str, dict[str, Rollable]] = Field(default_factory=dict)

    def __init__(self, **data):
        rollables = data.get("rollables", {})
        if rollables:
            data["rollables"] = {
                action: {name: Rollable.model_validate(r) for name, r in rmap.items()}
                for action, rmap in rollables.items()
            }
        super().__init__(**data)

    @property
    def actions(self) -> dict[str, Rollable] | None:
        return self.rollables.get("action")

    @property
    def bonus_actions(self) -> dict[str, Rollable] | None:
        return self.rollables.get("bonus_action")

    @property
    def reactions(self) -> dict[str, Rollable] | None:
        return self.rollables.get("reaction")

    @property
    def free(self) -> dict[str, Rollable] | None:
        return self.rollables.get("free")

    @property
    def level(self) -> int:
        return sum(c.level for c in self.classes)

