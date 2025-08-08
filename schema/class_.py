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

    def __init__(self, **data):
        rollables = data.get("rollables", {})
        if rollables:
            data["rollables"] = {k: Rollable.model_validate(v) for k, v in rollables.items()}
        super().__init__(**data)

