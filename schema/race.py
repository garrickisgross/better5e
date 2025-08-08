from pydantic import BaseModel, Field
from uuid import UUID

from schema.primitives import Modifier
from schema.rollable import Rollable


class Race(BaseModel):
    features: list[UUID]
    modifiers: list[Modifier]
    rollables: dict[str, Rollable] = Field(default_factory=dict)

    def __init__(self, **data):
        rollables = data.get("rollables", {})
        if rollables:
            data["rollables"] = {k: Rollable.model_validate(v) for k, v in rollables.items()}
        super().__init__(**data)
