from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from models.rollable import Rollable
from models.modifier import Modifier

class Feature(BaseModel):
    id: int = uuid4().int
    name: str
    prerequisites: Optional[str] = None  # e.g., "Requires level 3"
    feature_type: str # e.g., "class feature", "racial feature", etc.
    description: Optional[str] = None
    action_type: Optional[str] = None  # e.g., "action", "bonus action", "reaction"
    uses: Optional[int] = None  # Number of uses per rest, if applicable
    recharge: Optional[str] = None  # e.g., "short rest", "long rest", "dawn", etc.
    granted_features: Optional[list[int]] = []
    granted_spells: Optional[list[int]] = []
    granted_items: Optional[list[int]] = []
    modifiers: Optional[list[Modifier]] = []
    rollable: Optional[Rollable] = None
    options: Optional[list[int]] = [] # IDs of optional sub-features
    choice_count: Optional[int] = 1 # Number of choices to make from options


