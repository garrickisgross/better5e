from pydantic import BaseModel, Field
from typing import Optional
from schema.rollable import Rollable

class Spell(BaseModel):
    level: int
    school: str
    casting_time: str
    range: str
    components: list[str]
    duration: str
    description: str
    higher_levels: Optional[str] = None
    ritual: bool = False
    concentration: bool = False
    materials: Optional[str] = None
    rollables: dict[str, Rollable] = Field(default_factory=dict)
