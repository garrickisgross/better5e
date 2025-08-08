import types
from types import SimpleNamespace
from uuid import uuid4
import pytest

from wrappers import live_object
from wrappers import character_wrapper as cw
from schema.primitives import Modifier


class DummyGameObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __getitem__(self, key):
        return getattr(self, key)
    def __setitem__(self, key, value):
        setattr(self, key, value)


class DummyDAO:
    def __init__(self):
        self.updated = None
    def update(self, obj):
        self.updated = obj


def create_live_object():
    game_obj = DummyGameObject(
        id=uuid4(),
        name="feat",
        type="feature",
        data={
            "description": "d",
            "modifiers": [],
            "stats": {"hp": 1},
            "obj": SimpleNamespace(val=1, inner=SimpleNamespace(val=2)),
        },
    )
    lo = live_object.LiveObject(game_obj)
    lo.dao = DummyDAO()
    return lo, game_obj


def test_set_data_success_and_process_change():
    lo, game_obj = create_live_object()
    lo.set_data("stats.hp", 5, "set")
    assert game_obj.data["stats"]["hp"] == 5
    assert lo.dao.updated is game_obj
    lo.set_data("stats.hp", 2, "add")
    assert game_obj.data["stats"]["hp"] == 7
    lo.set_data("obj.val", 9, "set")
    assert game_obj.data["obj"].val == 9
    lo.set_data("obj.inner.val", 4, "set")
    assert game_obj.data["obj"].inner.val == 4


def test_set_data_errors():
    lo, _ = create_live_object()
    with pytest.raises(AttributeError):
        lo.set_data("stats.missing.value", 1, "set")
    with pytest.raises(AttributeError):
        lo.set_data("stats.wis", 1, "set")
    with pytest.raises(AttributeError):
        lo.set_data("obj.missing.attr", 1, "set")
    with pytest.raises(AttributeError):
        lo.set_data("obj.missing", 1, "set")


def test_livecharacter_init_and_load_features(monkeypatch):
    monkeypatch.setattr(cw, "super", types.SimpleNamespace(__init__=lambda *_: None), raising=False)
    with pytest.raises(AttributeError):
        cw.LiveCharacter(None)

    set_mod = Modifier(target="stats.hp", op="set", value=1)
    add_mod = Modifier(target="stats.hp", op="add", value=2)
    grant_mod = Modifier(target="", op="grant", value=uuid4())
    bad_mod = SimpleNamespace(target="", op="oops", value=0)
    feat_valid = SimpleNamespace(modifiers=[set_mod, add_mod, grant_mod])
    feat_bad = SimpleNamespace(modifiers=[bad_mod])

    class DummyLC:
        def __init__(self):
            self.features = [feat_valid, feat_bad]
            self.set_calls = []
            self.grants = []
        def set_data(self, t, v, op):
            self.set_calls.append((t, v, op))
        def grant(self, value):
            self.grants.append(value)

    dummy = DummyLC()
    with pytest.raises(ValueError):
        cw.LiveCharacter.load_features(dummy)
    assert dummy.set_calls[0] == ("stats.hp", 1, "set")
    assert dummy.set_calls[1] == ("stats.hp", 2, "add")
    assert dummy.grants == [grant_mod.value]

    cw.LiveCharacter.grant(dummy, uuid4())
