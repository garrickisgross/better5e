import random
import pytest

from schema.rollable import Rollable


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
    r = Rollable('2f6')
    with pytest.raises(ValueError):
        r.roll()


def test_invalid_input_type():
    with pytest.raises(TypeError):
        Rollable(3.5)
