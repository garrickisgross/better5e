from typing import Literal
from primitives import Asset, FeatureData, SpellData, ItemData, ClassData, SubClassData, ResourceData

class Feature(Asset):
    type: Literal["feature"] = "feature"
    data: FeatureData

class Spell(Asset):
    type: Literal["spell"] = "spell"
    data: SpellData

class Item(Asset):
    type: Literal["item"] = "item"
    data: ItemData

class Class(Asset):
    type: Literal["class"] = "class"
    data: ClassData

class Subclass(Asset):
    type: Literal["subclass"] = "subclass"
    data: SubClassData

class Resource(Asset):
    type: Literal["resource"] = "resource"
    data: ResourceData