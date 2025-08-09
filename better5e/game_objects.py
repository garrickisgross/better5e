from pydantic import BaseModel, Field
from typing import Literal, Any, Optional, Union
from uuid import UUID, uuid4

class Modifier(BaseModel):
    target: str
    op: Literal["add", "set", "grant", "return"]
    value: Union[int, UUID]

class Rollable(BaseModel):
    num_dice: int
    sides: int
    modifier: Modifier


class GameObject(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["feature", "class", "subclass", "item"]
    data: dict[str, Any] = Field(default_factory=dict)
    modifiers: list[Modifier] = Field(default_factory=list)
    grants: list[UUID] = Field(default_factory=list)
    actions: list[dict[str, Optional[Rollable]]] = Field(default_factory=list)
    