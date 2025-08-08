from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Any, Dict

class GameObject(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    data: Dict[str, Any]
    type: str
    tags: list[str] = Field(default_factory=list)

    