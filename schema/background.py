from pydantic import BaseModel, Field
from schema.primitives import Modifier
from schema.rollable import Rollable


class Background(BaseModel):
    description: str
    modifiers: list[Modifier]
    rollables: dict[str, Rollable] = Field(default_factory=dict)
