import pytest
from uuid import uuid4
from pydantic import ValidationError

from schema.primitives import AbilityScore, Skill, Modifier
from schema.feature import Feature
from schema.background import Background
from schema.character import Character, CharacterClass
from schema.class_ import Class
from schema.subclass import Subclass
from schema.factory import hydrate
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
    char = Character(
        ac=10,
        ability_scores=ability_scores,
        proficiency_bonus=2,
        skills=skills,
        background=background_id,
        features=[],
        inventory=[],
        classes=[class_entry],
        spellcasting=None,
    )
    assert char.classes[0].level == 1

    cls = Class(hit_die=8, features={1: [uuid4()]}, subclasses=[])
    assert cls.hit_die == 8

    subcls = Subclass(parent=uuid4(), features={1: [uuid4()]})
    assert subcls.features

    game_obj_char = GameObject(name="hero", type="character", data=char.dict())
    hydrated = hydrate(game_obj_char)
    assert isinstance(hydrated, Character)
    assert hydrated.background == background_id

    bg_obj = GameObject(name="acolyte", type="background", data={"description": "y", "modifiers": []})
    assert isinstance(hydrate(bg_obj), Background)

    unknown = GameObject(name="mystery", type="mystery", data={})
    with pytest.raises(ValueError):
        hydrate(unknown)
