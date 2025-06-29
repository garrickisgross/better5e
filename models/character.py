from pydantic import BaseModel
from typing import Optional, List
from models.feature import Feature
from models.item import Item
from models.classes import Class
from models.spell import Spell

class Character(BaseModel):
    """Represents a character in the game with various attributes and abilities."""
    name: str
    _class: Class
    level: int
    features: Optional[List[Feature]] = None
    items: Optional[List[Item]] = None
    spells: Optional[List[Spell]] = None
    attributes: Optional[dict[str, int]] = None  # e.g., {'strength': 10, 'dexterity': 12, ...}
    skills: Optional[dict[str, int]] = None  # e.g., {'acrobatics': 5, 'stealth': 3, ...}
    hit_points: Optional[int] = None  # Current hit points
    max_hit_points: Optional[int] = None  # Maximum hit points
    armor_class: Optional[int] = None  # Armor Class
    initiative: Optional[int] = None  # Initiative bonus
    speed: Optional[int] = None  # Speed in feet

