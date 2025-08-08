from pydantic import BaseModel, Field
from uuid import UUID

from schema.primitives import Modifier
from schema.rollable import Rollable


class Race(BaseModel):
    features: list[UUID]
    modifiers: list[Modifier]
    rollables: dict[str, Rollable] = Field(default_factory=dict)
