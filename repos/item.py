from database import BaseRepo
from models.item import Item, Weapon, Armor, Consumable, Tool

class ItemRepo(BaseRepo):
    TABLE = "items"
    MODEL = Item
    JSON_COLS = ["granted_features", "granted_spells", "granted_items"]

class WeaponRepo(ItemRepo):
    TABLE = "weapons"
    MODEL = Weapon
    JSON_COLS = ["granted_features", "granted_spells", "granted_items", "modifiers"]

class ArmorRepo(ItemRepo):
    TABLE = "armors"
    MODEL = Armor
    JSON_COLS = ["granted_features", "granted_spells", "granted_items"]

class ConsumableRepo(ItemRepo):
    TABLE = "consumables"
    MODEL = Consumable
    JSON_COLS = ["granted_features", "granted_spells", "granted_items", "rollable"]

class ToolRepo(ItemRepo):
    TABLE = "tools"
    MODEL = Tool  
    JSON_COLS = ["granted_features", "granted_spells", "granted_items"]
