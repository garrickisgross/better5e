from pydantic import BaseModel
from typing import Optional, List
from models.rollable import Rollable
from enum import Enum

class Components(str, Enum):
    """Enum for spell components."""
    VERBAL = "V"
    SOMATIC = "S"
    MATERIAL = "M"

class Spell(BaseModel):
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: List[Components]
    duration: str
    description: str
    damage: Optional[Rollable] = None
    healing: Optional[Rollable] = None
    effects: Optional[List[str]] = None
