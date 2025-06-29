from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

class Character(BaseModel):
    id: int = uuid4().int
    name: str
    level: int
    class_id: Optional[list[int]] = None
    subclass_id: Optional[list[int]] = None
    background_id: Optional[int] = None
    abilities: dict[str, int]  # e.g., {"strength": 10, "dexterity": 14, ...}
    skills: Optional[dict[str, int]] = None  # e.g., {"acrobatics": 2, "stealth": 3, ...}
    features: Optional[list[int]] = []  # List of feature IDs
    items: Optional[list[int]] = []  # List of item IDs
    hit_points: Optional[int] = None
    max_hit_points: Optional[int] = None
    temp_hit_points: Optional[int] = None
    equipped_items: Optional[list[int]] = []  # List of equipped item IDs

    