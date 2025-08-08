from better5e.game_objects import (
    GameObject,
    Feature,
    Item,
    Spell,
    Race,
    Background,
    CharacterClass,
)


def test_game_object_subclasses():
    base = GameObject(name="Base", type="base")
    assert base.type == "base"

    feature = Feature(name="Feat")
    item = Item(name="Item")
    spell = Spell(name="Spell")
    race = Race(name="Race")
    background = Background(name="Background")
    char_class = CharacterClass(name="Class")

    assert feature.type == "feature"
    assert item.type == "item"
    assert spell.type == "spell"
    assert race.type == "race"
    assert background.type == "background"
    assert char_class.type == "class"
