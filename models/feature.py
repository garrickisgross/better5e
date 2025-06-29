from pydantic import BaseModel, Field
from models.modifier import Modifier
from typing import Optional, Self
from models.item import Item
from models.spell import Spell

class Feature(BaseModel):
    name: str
    description: str
    modifiers: Optional[list[Modifier]]
    features: Optional[list[Self]]
    items: Optional[list[Item]]
    spells: Optional[list[Spell]]


