from pydantic import BaseModel
from uuid import UUID


class Subclass(BaseModel):
    parent: UUID
    features: dict[int, list[UUID]]

