from pydantic import BaseModel
from typing import Dict, Optional
from uuid import UUID

class Spellcasting(BaseModel):
    ability: str
    spell_list: list[UUID]
    slots: Dict[int, Dict[int, int]]
    spells_known: Optional[Dict[int, int]] = None
    cantrips_known: Optional[Dict[int, int]] = None
