import pytest
from better5e.rollable import _parse_expression, Roll
from better5e.modifiers import Modifier, ModifierOperation


def test_parse_expression_valid():
    assert _parse_expression("2d6+3") == (2, 6, 3)
    assert _parse_expression("d20-1") == (1, 20, -1)


def test_parse_expression_invalid():
    with pytest.raises(ValueError):
        _parse_expression("bad")


def test_roll_evaluate(monkeypatch):
    roll = Roll("2d6")
    monkeypatch.setattr(roll, "_roll_once", lambda: 7)
    assert roll.evaluate() == 7


def test_roll_advantage_disadvantage(monkeypatch):
    roll = Roll("1d20", advantage=True)
    values = iter([5, 15])
    monkeypatch.setattr(roll, "_roll_once", lambda: next(values))
    assert roll.evaluate() == 15

    roll = Roll("1d20", disadvantage=True)
    values = iter([5, 15])
    monkeypatch.setattr(roll, "_roll_once", lambda: next(values))
    assert roll.evaluate() == 5

    roll = Roll("1d20", advantage=True, disadvantage=True)
    values = iter([2, 18])
    monkeypatch.setattr(roll, "_roll_once", lambda: next(values))
    assert roll.evaluate() == 18


def test_roll_with_modifier(monkeypatch):
    roll = Roll("1d20")
    monkeypatch.setattr(roll, "_roll_once", lambda: 10)
    mod = Modifier(target="roll", operation=ModifierOperation.ADD, value=2)
    assert roll.evaluate([mod]) == 12
    other = Modifier(target="other", operation=ModifierOperation.ADD, value=5)
    assert roll.evaluate([other]) == 10

def test_roll_once(monkeypatch):
    roll = Roll("2d4+1")
    values = iter([1, 3])
    monkeypatch.setattr("random.randint", lambda a, b: next(values))
    assert roll._roll_once() == 1 + 3 + 1
