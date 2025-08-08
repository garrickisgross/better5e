from pydantic import BaseModel, Field
from typing import Dict, Optional
from uuid import UUID
from schema.rollable import Rollable

class Spellcasting(BaseModel):
    ability: str
    spell_list: list[UUID]
    slots: Dict[int, Dict[int, int]]
    spells_known: Optional[Dict[int, int]] = None
    cantrips_known: Optional[Dict[int, int]] = None
    rollables: dict[str, Rollable] = Field(default_factory=dict)
