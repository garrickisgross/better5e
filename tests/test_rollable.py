import random
import pytest
from uuid import uuid4

from schema.rollable import Rollable
from schema.character import Character, CharacterClass


def test_roll_int(monkeypatch):
    monkeypatch.setattr(random, 'randint', lambda a, b: 15)
    assert Rollable(5).roll() == 20


def test_roll_negative_int(monkeypatch):
    monkeypatch.setattr(random, 'randint', lambda a, b: 4)
    assert Rollable(-2).roll() == 2


def test_roll_dice(monkeypatch):
    r = Rollable('2d6+3')
    seq = iter([4, 5])
    monkeypatch.setattr(random, 'randint', lambda a, b: next(seq))
    assert r.roll() == 4 + 5 + 3


def test_roll_single_die(monkeypatch):
    r = Rollable('d8')
    monkeypatch.setattr(random, 'randint', lambda a, b: 6)
    assert r.roll() == 6


def test_invalid_notation():
    with pytest.raises(ValueError):
        Rollable('2f6')


def test_invalid_input_type():
    with pytest.raises(TypeError):
        Rollable(3.5)


def test_roll_with_character_modifier(monkeypatch):
    ability_scores = {"str": {"proficient": True, "value": 10, "modifier": 2}}
    char = Character(
        ac=10,
        ability_scores=ability_scores,
        proficiency_bonus=2,
        skills={},
        background=uuid4(),
        race=uuid4(),
        features=[],
        inventory=[],
        classes=[CharacterClass(class_id=uuid4(), level=1)],
    )
    r = Rollable({"dice": "1d20", "modifier": "str"})
    monkeypatch.setattr(random, 'randint', lambda a, b: 10)
    assert r.roll(char) == 12


def test_rollable_positional_and_keyword():
    with pytest.raises(TypeError):
        Rollable("1d6", modifier=2)


def test_rollable_model_validate_and_reuse():
    r = Rollable.model_validate("2d4+1")
    r2 = Rollable(r)
    assert r2.dice == r.dice


def test_rollable_model_validator_direct():
    assert Rollable._validate_before("1d4") == {"dice": "1d4", "modifier": 0}


def test_rollable_numeric_string():
    r = Rollable("7")
    assert r.dice == "1d20" and r.modifier == 7


def test_rollable_invalid_roll():
    r = Rollable(dice="1f6")
    with pytest.raises(ValueError):
        r.roll()


def test_rollable_modifier_requires_character():
    r = Rollable(dice="1d20", modifier="str")
    with pytest.raises(ValueError):
        r.roll()


def test_rollable_modifier_skill(monkeypatch):
    class Dummy:
        skills = {"stealth": type("Skill", (), {"modifier": 2})()}

    r = Rollable(dice="1d20", modifier="stealth")
    monkeypatch.setattr(random, 'randint', lambda a, b: 1)
    assert r.roll(Dummy()) == 3


def test_rollable_modifier_attribute(monkeypatch):
    class Dummy:
        ability_scores = {}
        skills = {}
        my_attr = 3

    r = Rollable(dice="1d20", modifier="my_attr")
    monkeypatch.setattr(random, 'randint', lambda a, b: 1)
    assert r.roll(Dummy()) == 4


def test_rollable_modifier_unknown(monkeypatch):
    class Dummy:
        ability_scores = {}
        skills = {}

    r = Rollable(dice="1d20", modifier="unknown")
    monkeypatch.setattr(random, 'randint', lambda a, b: 1)
    with pytest.raises(ValueError):
        r.roll(Dummy())


def test_rollable_modifier_type_error(monkeypatch):
    r = Rollable("1d6")
    r.__dict__["modifier"] = object()
    monkeypatch.setattr(random, 'randint', lambda a, b: 1)
    with pytest.raises(TypeError):
        r.roll(object())
