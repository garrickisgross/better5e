from database import BaseRepo
from models.classes import Class

class ClassRepo(BaseRepo):
    TABLE = "classes"
    MODEL = Class
    JSON_COLS = ["spells_know_by_level", "spell_slots_by_level", "allowed_spells", "features_by_level", "subclass_options"]

class SubclassRepo(BaseRepo):
    TABLE = "subclasses"
    MODEL = Class
    JSON_COLS = ["granted_spells", "features_by_level"]