from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

class Class(BaseModel):
    id: int = uuid4().int
    name: str
    description: Optional[str] = None
    hit_die: int
    spellcasting_ability: Optional[str] = None
    spellcasting_type: Optional[str] = None  # e.g., "prepared", "known"
    spells_known_by_level: Optional[dict[int, list[int]]] = None  # Level to list of spell IDs
    allowed_spells: Optional[list[int]] = None  # List of allowed spell IDs
    spell_slots_by_level: Optional[dict[int, dict[int, int]]] = None  # Level to (Spell Level to Number of Slots)
    features_by_level: Optional[dict[int, list[int]]] = None  # Level to list of feature IDs
    subclass_choice_level: Optional[int] = None  # Level at which subclass is chosen
    subclass_options: Optional[list[int]] = None  # List of subclass feature IDs

class Subclass(BaseModel):
    id: int = uuid4().int
    name: str
    parent_class_id: int  # ID of the parent class
    description: Optional[str] = None
    features_by_level: Optional[dict[int, list[int]]] = None  # Level to list of feature IDs
    granted_spells: Optional[list[int]] = None  # List of granted spell IDs
