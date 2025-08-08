from pydantic import BaseModel, Field
from uuid import UUID

from schema.rollable import Rollable


class Subclass(BaseModel):
    parent: UUID
    features: dict[int, list[UUID]]
    rollables: dict[str, Rollable] = Field(default_factory=dict)

