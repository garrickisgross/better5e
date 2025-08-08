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
from store.game_obj import GameObject

def test_primitives_and_feature():
    ability = AbilityScore(proficient=True, value=15, modifier=2)
    assert ability.value == 15
    skill = Skill(proficient="expert", modifier=3)
    modifier = Modifier(target="stats.hp", op="add", value=5)
    feat = Feature(description="x", modifiers=[modifier])
    assert feat.description == "x"

    bg = Background(description="y", modifiers=[modifier])
    assert bg.modifiers[0].op == "add"

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
    )
    assert char.classes[0].level == 1

    cls = Class(hit_die=8, features={1: [uuid4()]}, subclasses=[])
    assert cls.hit_die == 8

    subcls = Subclass(parent=uuid4(), features={1: [uuid4()]})
    assert subcls.features

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
    )
    assert spell.level == 1

    spell_list = [uuid4(), uuid4()]
    slots = {1: {1: 2}, 2: {1: 3, 2: 1}}
    sc = Spellcasting(ability="int", spell_list=spell_list, slots=slots)
    assert sc.slots[2][2] == 1

    sc_obj = GameObject(name="Wizard Spellcasting", type="spellcasting", data=sc.model_dump())
    spell_obj = GameObject(name="Fire Bolt", type="spell", data=spell.model_dump())

    hydrated_sc = hydrate(sc_obj)
    hydrated_spell = hydrate(spell_obj)

    assert isinstance(hydrated_sc, Spellcasting)
    assert isinstance(hydrated_spell, Spell)

    cls = Class(hit_die=6, features={1: [uuid4()]}, subclasses=[], spellcasting=sc_obj.id)
    assert cls.spellcasting == sc_obj.id
    mod = Modifier(target="stats.speed", op="set", value=30)
    race = Race(features=[uuid4()], modifiers=[mod])
    game_obj_race = GameObject(name="elf", type="race", data=race.model_dump())
    hydrated_race = hydrate(game_obj_race)
    assert isinstance(hydrated_race, Race)
