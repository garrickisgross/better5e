from pydantic import BaseModel
from pydantic.types import Literal

class SaveModifier(BaseModel):
    """ Represents a skill modifier in the system. """
    save: str
    modifier: int = 0
    type: Literal["proficiency", "modifier"] = "modifier"
