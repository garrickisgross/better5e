from database import BaseRepo
from models.spell import Spell

class SpellRepo(BaseRepo):
    TABLE = "spells"
    MODEL = Spell
    JSON_COLS = ["components", "damage"]