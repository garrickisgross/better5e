from pydantic import BaseModel
from uuid import UUID

from schema.primitives import Modifier


class Race(BaseModel):
    features: list[UUID]
    modifiers: list[Modifier]
