import pytest
from uuid import uuid4
from pydantic import ValidationError

from schema.primitives import AbilityScore, Skill, Modifier
from schema.feature import Feature
from schema.background import Background
from schema.character import Character, CharacterClass
from schema.class_ import Class
from schema.subclass import Subclass
from schema.spell import Spell
from schema.spellcasting import Spellcasting
from schema.factory import hydrate
from schema.race import Race
from schema.item import Item
from schema.rollable import Rollable
from store.game_obj import GameObject

def test_primitives_and_feature():
    ability = AbilityScore(proficient=True, value=15, modifier=2)
    assert ability.value == 15
    skill = Skill(proficient="expert", modifier=3)
    modifier = Modifier(target="stats.hp", op="add", value=5)
    feat = Feature(description="x", modifiers=[modifier], rollables={"action": "1d20"})
    assert feat.description == "x"
    assert isinstance(feat.rollables["action"], Rollable)

    bg = Background(description="y", modifiers=[modifier], rollables={"luck": "1d4"})
    assert bg.modifiers[0].op == "add"
    assert isinstance(bg.rollables["luck"], Rollable)

    with pytest.raises(ValidationError):
        Skill(proficient="invalid", modifier=0)


def test_character_and_related_models_and_hydrate():
    ability_scores = {"str": {"proficient": True, "value": 10, "modifier": 0}}
    skills = {"acrobatics": {"proficient": "none", "modifier": 0}}
    class_entry = {"class_id": uuid4(), "level": 1}
    background_id = uuid4()
    race_id = uuid4()
    char = Character(
        ac=10,
        ability_scores=ability_scores,
        proficiency_bonus=2,
        skills=skills,
        background=background_id,
        race=race_id,
        features=[],
        inventory=[],
        classes=[class_entry],
        rollables={
            "action": {"base": "1d20"},
            "bonus_action": {"base": 5},
            "reaction": {"counter": "1d6"},
            "free": {"shout": "1d4"},
        },
    )
    assert isinstance(char.actions["base"], Rollable)
    assert isinstance(char.bonus_actions["base"], Rollable)
    assert isinstance(char.reactions["counter"], Rollable)
    assert isinstance(char.free["shout"], Rollable)
    assert char.classes[0].level == 1

    cls = Class(hit_die=8, features={1: [uuid4()]}, subclasses=[], rollables={"action": "1d6"})
    assert isinstance(cls.rollables["action"], Rollable)

    subcls = Subclass(parent=uuid4(), features={1: [uuid4()]}, rollables={"action": "1d4"})
    assert isinstance(subcls.rollables["action"], Rollable)

    game_obj_char = GameObject(name="hero", type="character", data=char.model_dump())
    hydrated = hydrate(game_obj_char)
    assert isinstance(hydrated, Character)
    assert hydrated.background == background_id

    bg_obj = GameObject(name="acolyte", type="background", data={"description": "y", "modifiers": []})
    assert isinstance(hydrate(bg_obj), Background)
    assert hydrated.race == race_id

    unknown = GameObject(name="mystery", type="mystery", data={})
    with pytest.raises(ValueError):
        hydrate(unknown)

def test_spell_and_spellcasting_and_mount():
    spell = Spell(
        level=1,
        school="evocation",
        casting_time="1 action",
        range="60 feet",
        components=["V", "S"],
        duration="Instantaneous",
        description="A bolt of fire",
        rollables={"damage": "1d8"},
    )
    assert isinstance(spell.rollables["damage"], Rollable)

    spell_list = [uuid4(), uuid4()]
    slots = {1: {1: 2}, 2: {1: 3, 2: 1}}
    sc = Spellcasting(ability="int", spell_list=spell_list, slots=slots, rollables={"save": "1d20"})
    assert isinstance(sc.rollables["save"], Rollable)

    sc_obj = GameObject(name="Wizard Spellcasting", type="spellcasting", data=sc.model_dump())
    spell_obj = GameObject(name="Fire Bolt", type="spell", data=spell.model_dump())

    hydrated_sc = hydrate(sc_obj)
    hydrated_spell = hydrate(spell_obj)

    assert isinstance(hydrated_sc, Spellcasting)
    assert isinstance(hydrated_spell, Spell)

    cls = Class(hit_die=6, features={1: [uuid4()]}, subclasses=[], spellcasting=sc_obj.id)
    assert cls.spellcasting == sc_obj.id
    mod = Modifier(target="stats.speed", op="set", value=30)
    race = Race(features=[uuid4()], modifiers=[mod], rollables={"sprint": "1d4"})
    assert isinstance(race.rollables["sprint"], Rollable)
    game_obj_race = GameObject(name="elf", type="race", data=race.model_dump())
    hydrated_race = hydrate(game_obj_race)
    assert isinstance(hydrated_race, Race)


def test_item_and_hydrate():
    mod = Modifier(target="stats.hp", op="add", value=5)
    item = Item(
        category="weapon",
        equipped=True,
        modifiers=[mod],
        attack_modifier=1,
        damage_dice="1d6",
        damage_modifier=2,
        rollables={"action": "1d6"},
    )
    assert item.equipped
    assert isinstance(item.rollables["action"], Rollable)
    assert item.attack_modifier == 1
    assert item.damage_dice == "1d6"
    assert item.damage_modifier == 2
    game_obj_item = GameObject(name="Sword", type="item", data=item.model_dump())
    hydrated_item = hydrate(game_obj_item)
    assert isinstance(hydrated_item, Item)
    assert hydrated_item.attack_modifier == 1
    assert hydrated_item.damage_dice == "1d6"
    assert hydrated_item.damage_modifier == 2
