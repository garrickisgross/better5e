from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from models.modifier import Modifier
from models.rollable import Rollable

class Spell(BaseModel):
    id: int = uuid4().int
    name: str
    level: int  # Spell level (0 for cantrips)
    school: str  # e.g., "evocation", "illusion", etc.
    casting_time: str  # e.g., "1 action", "1 bonus action", etc.
    range: str  # e.g., "60 feet", "self", etc.
    components: list[str]  # e.g., ["V", "S", "M"]
    duration: str  # e.g., "1 minute", "instantaneous"
    description: Optional[str] = None
    higher_level_effects: Optional[Modifier] = None
    material_components: Optional[str] = None  # e.g., "a pinch of powdered iron"
    ritual: Optional[bool] = False  # Whether the spell can be cast as a
    damage: Optional[Rollable] = None  # Damage rollable object if applicable
    area_of_effect: Optional[str] = None  # e.g., "20-foot radius"
    saving_throw: Optional[str] = None  # e.g., "Dexterity", "Constitution"
    

    def __str__(self):
        return f"{self.name} (Level {self.level}) - {self.school} - {self.description}"