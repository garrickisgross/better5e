from pydantic import BaseModel, Field
from typing import Literal, Any, Optional, Union
from uuid import UUID, uuid4


class Modifier(BaseModel):
    target: str
    op: Literal["add", "set", "get"]
    value: int

class Grant(BaseModel):
    choice: int
    options: list[UUID]

class Rollable(BaseModel):
    num: int
    sides: int
    modifiers: Optional[list[Modifier]] = None # really modifier should only 'get' a value from the character sheet here. Find a way to validate that. 

class Action(BaseModel):
    type: Literal["action", "bonus_action", "reaction", "passive", "free"]
    roll: Optional[Rollable] = None

class Resource(BaseModel):
    uses_max: int
    uses_current: int
    actions: Optional[list[Action]] = []

class GameObj(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    desc: str
    kind: str
    modifiers: Optional[list[Modifier]] = []
    grants: Optional[list[Grant]] = []
    actions: Optional[list[Action]] = []
    resources: Optional[list[Resource]] = []







    