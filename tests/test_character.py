import pytest
from better5e.character import Character
from better5e.game_objects import (
    Feature,
    Item,
    Spell,
    Race,
    Background,
    CharacterClass,
    GameObject,
)
from better5e.modifiers import Modifier, ModifierOperation


class DummyDAO:
    def __init__(self, objects):
        self.objects = {obj.uuid: obj for obj in objects}

    def load(self, obj_id):
        return self.objects[obj_id]


def test_all_game_objects_and_modifiers():
    feature = Feature(name="Feat")
    feature.modifiers.append(
        Modifier(target="stats.strength", operation=ModifierOperation.ADD, value=2)
    )
    item = Item(name="Item")
    spell = Spell(name="Spell")
    race = Race(name="Race")
    background = Background(name="Background")
    char = Character(
        name="Hero",
        race=race,
        background=background,
        features=[feature],
        items=[item],
        spells=[spell],
    )
    objs = list(char.all_game_objects())
    assert set(o.uuid for o in objs) == {
        race.uuid,
        background.uuid,
        feature.uuid,
        item.uuid,
        spell.uuid,
    }
    mods = list(char.all_modifiers())
    assert mods[0].value == 2


def test_get_stat_with_modifiers():
    feature_add = Feature(
        name="Add",
        modifiers=[
            Modifier(
                target="stats.strength", operation=ModifierOperation.ADD, value=2
            )
        ],
    )
    feature_set = Feature(
        name="Set",
        modifiers=[
            Modifier(
                target="stats.strength", operation=ModifierOperation.SET, value=15
            )
        ],
    )
    feature_grant = Feature(
        name="Grant",
        modifiers=[
            Modifier(
                target="stats.strength", operation=ModifierOperation.GRANT, value=99
            )
        ],
    )
    char = Character(name="Hero", features=[feature_add, feature_set, feature_grant])
    assert char.get_stat("strength") == 15
    assert char.get_stat("dexterity") == 10


def test_add_game_object():
    char = Character(name="Hero")
    feature = Feature(name="Feat")
    item = Item(name="Item")
    spell = Spell(name="Spell")
    race = Race(name="Race")
    background = Background(name="Background")
    char_class = CharacterClass(name="Class")

    char.add_game_object(feature)
    char.add_game_object(item)
    char.add_game_object(spell)
    char.add_game_object(race)
    char.add_game_object(background)
    char.add_game_object(char_class)
    char.add_game_object(char_class)

    assert char.features == [feature]
    assert char.items == [item]
    assert char.spells == [spell]
    assert char.race == race
    assert char.background == background
    assert char.classes[char_class.uuid] == 2

    with pytest.raises(TypeError):
        char.add_game_object(GameObject(name="Unknown", type="unknown"))


def test_apply_grants_cycle():
    feature1 = Feature(name="Feat1")
    feature2 = Feature(name="Feat2")
    feature1.grants.append(feature2.uuid)
    feature2.grants.append(feature1.uuid)
    race = Race(name="Race", grants=[feature1.uuid])
    dao = DummyDAO([feature1, feature2])
    char = Character(name="Hero", race=race)
    char.apply_grants(dao)
    assert feature1 in char.features
    assert feature2 in char.features
