from pydantic import BaseModel
import uuid
from typing import Optional
from models.resource import Resource
from models.spell import Spell
from models.feature import Feature

class Item(BaseModel):
    """ Represents an item in the system. """
    id: uuid.UUID = uuid.uuid4()  # Default to a new UUID
    name: str
    description: str = ""
    weight: float = 0.0 
    value: float = 0.0  

    # an item can have a resource tied to it.
    resource: Optional[Resource] = None

    # an item can grant a spell.
    spells: list[Spell] = []

    # an item can grant a spell with charges.
    spells_with_charges: list[tuple[Spell, int]] = []

    # an item can grant a feature.
    features: list[Feature] = []

    # an item can be a weapon.
    is_weapon: bool = False

    


