from better5e.factory import create_game_object
from better5e.game_objects import (
    Feature,
    Item,
    Spell,
    Race,
    Background,
    CharacterClass,
    GameObject,
)


def test_create_game_object_known_types():
    mapping = {
        "feature": Feature,
        "item": Item,
        "spell": Spell,
        "race": Race,
        "background": Background,
        "class": CharacterClass,
    }
    for type_name, cls in mapping.items():
        data = {"name": type_name, "type": type_name}
        obj = create_game_object(data)
        assert isinstance(obj, cls)


def test_create_game_object_unknown_type():
    data = {"name": "Mystery", "type": "mystery"}
    obj = create_game_object(data)
    assert isinstance(obj, GameObject)
    assert obj.type == "mystery"
