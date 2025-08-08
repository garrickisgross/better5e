from pydantic import BaseModel
from schema.primitives import Modifier


class Background(BaseModel):
    description: str
    modifiers: list[Modifier]
