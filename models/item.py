from uuid import uuid4
from pydantic import BaseModel
from typing import Optional
from models.rollable import Rollable
from models.modifier import Modifier

class Item(BaseModel):
    id: int = uuid4().int
    name: str
    action_type: Optional[str] = None
    item_type: str  # e.g., "weapon", "armor", "consumable", "tool"
    rarity: Optional[str] = None  # e.g., "common", "uncommon", "rare", "very rare", "legendary"
    description: Optional[str] = None
    weight: Optional[float] = None
    value: Optional[float] = None
    requires_attunement: Optional[bool] = False
    granted_features: Optional[list[int]] = []
    granted_spells: Optional[list[int]] = []
    granted_items: Optional[list[int]] = []


class Weapon(Item):
    attack_type: str
    damage: Rollable
    range: str
    attack: Rollable
    damage_type: str
    magic_bonus: Optional[int] = 0
    modifiers: Optional[list[Modifier]] = []

class Armor(Item):
    base_ac: int
    max_dex_bonus: Optional[int] = None

class Consumable(Item):
    rollable: Optional[Rollable] = None
    duration: Optional[int] = None
    uses: Optional[int] = 1

class Tool(Item):
    tool_type: str
    proficiency_required: Optional[bool] = False





