from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class Class(BaseModel):
    hit_die: int
    features: dict[int, list[UUID]]
    subclasses: list[UUID]
    spellcasting: Optional[UUID] = None

