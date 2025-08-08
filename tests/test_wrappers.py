import types
from types import SimpleNamespace
from uuid import uuid4
import pytest

from wrappers import live_object
from wrappers import character_wrapper as cw
from schema.primitives import Modifier
from schema.spell import Spell
from schema.spellcasting import Spellcasting
from schema.class_ import Class
from schema.character import Character, CharacterClass
from store.game_obj import GameObject
from schema.factory import hydrate


class DummyGameObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __getitem__(self, key):
        return getattr(self, key)
    def __setitem__(self, key, value):
        setattr(self, key, value)


class DummyDAO:
    def __init__(self, objects=None):
        self.updated = None
        self.objects = objects or {}
    def update(self, obj):
        self.updated = obj
    def get_by_id(self, obj_id):
        return self.objects[obj_id]


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


def test_load_spellcasting():
    spell = Spell(
        level=1,
        school="evocation",
        casting_time="1 action",
        range="60 feet",
        components=["V", "S"],
        duration="Instantaneous",
        description="A bolt of fire",
    )
    spell_obj = GameObject(name="Fire Bolt", type="spell", data=spell.dict())

    sc = Spellcasting(ability="int", spell_list=[spell_obj.id], slots={1: {1: 2}})
    sc_obj = GameObject(name="Wizard Spellcasting", type="spellcasting", data=sc.dict())

    cls_model = Class(hit_die=6, features={}, subclasses=[], spellcasting=sc_obj.id)
    cls_obj = GameObject(name="Wizard", type="class", data=cls_model.dict())

    char_class = CharacterClass(class_id=cls_obj.id, level=1)
    character = Character(
        ac=10,
        ability_scores={},
        proficiency_bonus=2,
        skills={},
        features=[],
        inventory=[],
        classes=[char_class],
    )
    char_obj = GameObject(name="Hero", type="character", data=character.dict())

    objects = {
        cls_obj.id: cls_obj,
        sc_obj.id: sc_obj,
        spell_obj.id: spell_obj,
    }
    dummy = SimpleNamespace(
        dao=DummyDAO(objects),
        raw=char_obj,
        data=hydrate(char_obj),
        spells={},
    )

    def process_change(self):
        self.data = hydrate(self.raw)
        self.dao.update(self.raw)

    dummy.process_change = types.MethodType(process_change, dummy)

    cw.LiveCharacter.load_spellcasting(dummy)
    assert "Wizard" in dummy.data.spellcasting
    assert dummy.spells["Wizard"][0].description == "A bolt of fire"
