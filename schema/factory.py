from store.game_obj import GameObject
from schema.character import Character
from schema.feature import Feature
from schema.class_ import Class
from schema.subclass import Subclass
from schema.spell import Spell
from schema.spellcasting import Spellcasting
from schema.background import Background
from schema.race import Race

TYPE_MAP = {
    "character": Character,
    "class": Class,
    "subclass": Subclass,
    "background": Background,
    "race": Race,
    "feature": Feature,
    "item": None,
    "spell": Spell,
    "spellcasting": Spellcasting,
    "monster": None,
    "npc": None,
}

def hydrate(game_object: GameObject):
    cls = TYPE_MAP.get(game_object.type)
    if not cls:
        raise ValueError(f"Unknown type: {game_object.type}")
    return cls.model_validate(game_object.data)

