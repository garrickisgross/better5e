from pydantic import BaseModel
from typing import Any, Optional
from uuid import uuid4
from models.rollable import Rollable
from models.modifier import Modifier
from models.enums import FeatureType, ActionType




class Feature(BaseModel):
    id: int = uuid4().int
    name: str
    prerequisites: Optional[dict[str, Any]] = None  # mapping of prerequisite types to values, e.g., {"level": 5, "class": "fighter"}
    prerequisites_text: Optional[str] = None  # Textual description of prerequisites
    feature_type: FeatureType # e.g., "class feature", "racial feature", etc.
    action_type: Optional[ActionType] = ActionType.NONE  # e.g., "action", "bonus action", "reaction"
    description: Optional[str] = None
    uses: Optional[int] = None  # Number of uses per rest, if applicable
    recharge: Optional[str] = None  # e.g., "short rest", "long rest", "dawn", etc.
    granted_features: Optional[list[int]] = []
    granted_spells: Optional[list[int]] = []
    granted_items: Optional[list[int]] = []
    modifiers: Optional[list[Modifier]] = []
    rollable: Optional[Rollable] = None
    options: Optional[list[int]] = [] # IDs of optional sub-features
    choice_count: Optional[int] = 1 # Number of choices to make from options


