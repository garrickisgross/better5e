from pydantic import BaseModel
from typing import Optional
from models.rollable import Rollable
from models.feature import Feature

class Item(BaseModel):
    name: str
    description: str
    rarity: Optional[str] = None
    weight: Optional[float] = None
    value: Optional[int] = None
    features: Optional[list[Feature]] = None

class Weapon(Item):
    damage: Rollable
    damage_type: str
    attack: Rollable
    attack_bonus: int = 0
    

class Armor(Item):
    base_ac: int
    max_dex_bonus: Optional[int] = None
    stealth_disadvantage: bool = False

class Consumable(Item):
    uses: int = 1
    effect: str

