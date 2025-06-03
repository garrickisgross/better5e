import uuid
from pydantic import BaseModel

from typing import Self

from models.resource import Resource
from models.skill_modifier import SkillModifier
from models.save_modifier import SaveModifier
from models.attribute_modifier import AttributeModifier
from models.item import Item
from models.spell import Spell

class Feature(BaseModel):
    """ Represents a feature in the system. """
    id: uuid.UUID = uuid.uuid4() # Default to a new UUID
    name: str
    description: str

    # a feature can add one or more resources to a sheet.
    resources: list[Resource] = []

    # a feature can modify one or more skills on a sheet.
    skill_modifiers: list[SkillModifier] = []

    # a feature can modify one or more Saves on a sheet.
    save_modifiers: list[SaveModifier] = []

    # a feature can modify one or more attributes on a sheet.
    attribute_modifiers: list[AttributeModifier] = []

    # a feature can grant one or more items to a sheet. 
    items: list[Item] = []

    # a feature can grant one or more spells to a sheet.
    spells: list[Spell] = []

    # a feature can grant a spell with charges.
    spells_with_charges: list[tuple[Spell, int]] = []

    # a feature can grant one or more other features. 
    features: list[Self] = []


    
