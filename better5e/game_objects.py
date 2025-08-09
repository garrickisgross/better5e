from pydantic import BaseModel, Field
from typing import Literal, Any
from uuid import UUID, uuid4

class GameObject(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["feature", "class", "subclass", "item"]
    data: dict[str, Any] = Field(default_factory=dict)
    name: str
    modifiers: list[Modifier] = Field(default_factory=list)
    grants: list[UUID] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    