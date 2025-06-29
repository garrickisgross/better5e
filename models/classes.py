from typing import Optional
from pydantic import BaseModel
from models.feature import Feature
from models.spell import Spell
from models.classes import Class

class ClassFeature(Feature):
    """Class feature that can be used by a class."""
    level: int  # Level at which this feature is gained
    class_name: str  # Name of the class this feature belongs to

    def __str__(self):
        return f"{self.name} (Level {self.level}) - {self.description}"

class SpellTable(BaseModel):
    _class: Class
    spell_table: dict[int, list[Spell]]  

class Class(BaseModel):
    """Base class for all game classes."""
    name: str
    description: str
    hit_die: int
    saving_throws: list[str]
    proficiencies: list[str]
    features: list[ClassFeature] 
    spell_table = Optional[SpellTable] # List of feature names or IDs

    def __str__(self):
        return f"{self.name} - {self.description}"