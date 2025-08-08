from pydantic import BaseModel
from schema.primitives import Modifier

class Feature(BaseModel):
    description: str
    modifiers: list[Modifier]