from pydantic import BaseModel
from uuid import UUID


class Class(BaseModel):
    hit_die: int
    features: dict[int, list[UUID]]
    subclasses: list[UUID]

