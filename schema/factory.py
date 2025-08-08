from store.game_obj import GameObject
from schema.character import Character
from schema.feature import Feature

TYPE_MAP = {
    "character": Character,
    "class": None,
    "subclass": None,
    "race": None,
    "background": None,
    "feature": Feature,
    "item": None,
    "spell": None,
    "monster": None,
    "npc": None,
}

def hydrate(game_object: GameObject):
    cls = TYPE_MAP.get(game_object.type)
    if not cls:
        raise ValueError(f"Unknown type: {game_object.type}")
    return cls.parse_obj(game_object.data)