from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Any

from schema.primitives import AbilityScore, Skill

class Character(BaseModel):
    ac: int
    ability_scores: dict[str, AbilityScore]
    proficiency_bonus: int
    skills: dict[str, Skill]
    features: list[UUID]
    inventory: list[UUID]
    spellcasting: Optional[dict[Any, Any]] # change when we work on spellcasting object


