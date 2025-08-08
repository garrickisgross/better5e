from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

from schema.rollable import Rollable


class Class(BaseModel):
    hit_die: int
    features: dict[int, list[UUID]]
    subclasses: list[UUID]
    spellcasting: Optional[UUID] = None
    rollables: dict[str, Rollable] = Field(default_factory=dict)

