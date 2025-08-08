from pydantic import BaseModel
from typing import Literal, Union
from uuid import UUID

class AbilityScore(BaseModel):
    proficient: bool # for saves
    value: int
    modifier: int

class Skill(BaseModel):
    proficient: Literal["expert", "proficient", "half", "none"]
    modifier: int

class Modifier(BaseModel):
    target: str
    op: Literal["add", "set", "grant"]
    value: Union[int, UUID]