import types
from types import SimpleNamespace
from uuid import uuid4
from collections import deque
import pytest

from wrappers import live_object
from wrappers import character_wrapper as cw
from schema.primitives import Modifier
from schema.spell import Spell
from schema.spellcasting import Spellcasting
from schema.class_ import Class
from schema.character import Character, CharacterClass
from schema.feature import Feature
from schema.item import Item
from schema.background import Background
from schema.race import Race
from store.game_obj import GameObject
from schema.factory import hydrate
from store.game_obj import GameObject
import random


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
    lo.set_data("obj.val", 1, "add")
    assert game_obj.data["obj"].val == 10


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


def test_set_data_unsupported_op():
    lo, _ = create_live_object()
    with pytest.raises(ValueError):
        lo.set_data("obj.val", 1, "mul")
    with pytest.raises(ValueError):
        lo.set_data("stats.hp", 1, "mul")


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
    spell_obj = GameObject(name="Fire Bolt", type="spell", data=spell.model_dump())

    sc = Spellcasting(ability="int", spell_list=[spell_obj.id], slots={1: {1: 2}})
    sc_obj = GameObject(name="Wizard Spellcasting", type="spellcasting", data=sc.model_dump())

    cls_model = Class(hit_die=6, features={}, subclasses=[], spellcasting=sc_obj.id)
    cls_obj = GameObject(name="Wizard", type="class", data=cls_model.model_dump())

    cls_no_sc_model = Class(hit_die=8, features={}, subclasses=[], spellcasting=None)
    cls_no_sc_obj = GameObject(name="Fighter", type="class", data=cls_no_sc_model.model_dump())

    char_class = CharacterClass(class_id=cls_obj.id, level=1)
    char_class_no_sc = CharacterClass(class_id=cls_no_sc_obj.id, level=1)
    character = Character(
        ac=10,
        ability_scores={},
        proficiency_bonus=2,
        skills={},
        background=uuid4(),
        race=uuid4(),
        features=[],
        inventory=[],
        classes=[char_class, char_class_no_sc],
    )
    char_obj = GameObject(name="Hero", type="character", data=character.model_dump())

    objects = {
        cls_obj.id: cls_obj,
        sc_obj.id: sc_obj,
        spell_obj.id: spell_obj,
        cls_no_sc_obj.id: cls_no_sc_obj,
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
    assert "Fighter" not in dummy.spells

def test_livecharacter_apply_background(monkeypatch):
    set_mod = SimpleNamespace(target="stats.hp", op="set", value=1)
    add_mod = SimpleNamespace(target="stats.hp", op="add", value=2)
    grant_mod = SimpleNamespace(target="", op="grant", value=uuid4())
    bad_mod = SimpleNamespace(target="", op="oops", value=0)

    good_bg = SimpleNamespace(modifiers=[set_mod, add_mod, grant_mod])
    bad_bg = SimpleNamespace(modifiers=[bad_mod])

    class DummyLC:
        def __init__(self, bg_obj):
            self.dao = SimpleNamespace(get_by_id=lambda _id: bg_obj)
            self.data = SimpleNamespace(background=uuid4())
            self.set_calls = []
            self.grants = []

        def set_data(self, target, value, op):
            self.set_calls.append((target, value, op))

        def grant(self, value):
            self.grants.append(value)

    monkeypatch.setattr(cw, "hydrate", lambda x: x)

    dummy = DummyLC(good_bg)
    cw.LiveCharacter.apply_background(dummy)
    assert dummy.set_calls[0] == ("stats.hp", 1, "set")
    assert dummy.set_calls[1] == ("stats.hp", 2, "add")
    assert dummy.grants == [grant_mod.value]

    dummy_bad = DummyLC(bad_bg)
    with pytest.raises(ValueError):
        cw.LiveCharacter.apply_background(dummy_bad)

def test_load_features_includes_race(monkeypatch):
    set_mod = SimpleNamespace(target="stats.hp", op="set", value=1)
    race_mod = SimpleNamespace(target="stats.hp", op="add", value=2)
    race_grant = SimpleNamespace(target="", op="grant", value=uuid4())
    feat_obj = SimpleNamespace(modifiers=[set_mod])
    race_obj = SimpleNamespace(features=["feat"], modifiers=[race_mod, race_grant])

    class DummyDAO:
        def get_by_id(self, id):
            return {"feat": feat_obj, "race": race_obj}[id]

    class DummyLC:
        def __init__(self):
            self.features = []
            self.set_calls = []
            self.grants = []
            self.dao = DummyDAO()
            self.data = SimpleNamespace(features=[], race="race")


        def set_data(self, t, v, op):
            self.set_calls.append((t, v, op))

        def grant(self, value):
            self.grants.append(value)

    monkeypatch.setattr(cw, "hydrate", lambda x: x)
    dummy = DummyLC()
    dummy._load_race = types.MethodType(cw.LiveCharacter._load_race, dummy)
    cw.LiveCharacter.load_features(dummy)
    assert dummy.features == [feat_obj]
    assert ("stats.hp", 1, "set") in dummy.set_calls
    assert ("stats.hp", 2, "add") in dummy.set_calls
    assert dummy.grants == [race_grant.value]


def test_load_race_invalid_modifier(monkeypatch):
    bad_mod = SimpleNamespace(target="", op="oops", value=0)
    race_obj = SimpleNamespace(features=[], modifiers=[bad_mod])

    class DummyDAO:
        def get_by_id(self, _id):
            return race_obj

    class DummyLC:
        def __init__(self):
            self.features = []
            self.set_calls = []
            self.grants = []
            self.dao = DummyDAO()
            self.data = SimpleNamespace(race="race")

        def set_data(self, t, v, op):
            self.set_calls.append((t, v, op))

        def grant(self, value):
            self.grants.append(value)

    monkeypatch.setattr(cw, "hydrate", lambda x: x)
    with pytest.raises(ValueError):
        cw.LiveCharacter._load_race(DummyLC())


def test_load_items(monkeypatch):
    add_mod = SimpleNamespace(target="stats.hp", op="add", value=2)
    grant_mod = SimpleNamespace(target="", op="grant", value=uuid4())
    bad_mod = SimpleNamespace(target="", op="oops", value=0)
    item_eq = SimpleNamespace(equipped=True, modifiers=[add_mod, grant_mod])
    item_uneq = SimpleNamespace(equipped=False, modifiers=[add_mod])
    item_bad = SimpleNamespace(equipped=True, modifiers=[bad_mod])

    class DummyDAO:
        def __init__(self, objects):
            self.objects = objects
        def get_by_id(self, obj_id):
            return self.objects[obj_id]

    class DummyLC:
        def __init__(self, dao, inventory):
            self.items = []
            self.dao = dao
            self.data = SimpleNamespace(inventory=inventory)
            self.set_calls = []
            self.grants = []

        def set_data(self, t, v, op):
            self.set_calls.append((t, v, op))

        def grant(self, value):
            self.grants.append(value)

    monkeypatch.setattr(cw, "hydrate", lambda x: x)

    dummy = DummyLC(DummyDAO({"eq": item_eq, "uneq": item_uneq}), ["eq", "uneq"])
    cw.LiveCharacter.load_items(dummy)
    assert dummy.items == [item_eq, item_uneq]
    assert dummy.set_calls == [("stats.hp", 2, "add")]
    assert dummy.grants == [grant_mod.value]

    dummy_bad = DummyLC(DummyDAO({"bad": item_bad}), ["bad"])
    with pytest.raises(ValueError):
        cw.LiveCharacter.load_items(dummy_bad)


def test_livecharacter_rollables(monkeypatch):
    feature_id = uuid4()
    item_id = uuid4()
    bg_id = uuid4()
    race_id = uuid4()

    feature = Feature(description="f", modifiers=[], rollables={"action": "1d6"})
    item = Item(
        category="weapon",
        equipped=True,
        modifiers=[],
        attack_modifier=0,
        damage_dice="1d4",
        damage_modifier=0,
        rollables={"bonus_action": "1d4"},
    )
    background = Background(description="bg", modifiers=[], rollables={})
    race = Race(features=[], modifiers=[], rollables={})
    feature_obj = GameObject(id=feature_id, name="FeatRoll", type="feature", data=feature.model_dump())
    item_obj = GameObject(id=item_id, name="Sword", type="item", data=item.model_dump())
    bg_obj = GameObject(id=bg_id, name="Acolyte", type="background", data=background.model_dump())
    race_obj = GameObject(id=race_id, name="Elf", type="race", data=race.model_dump())

    char = Character(
        ac=10,
        ability_scores={},
        proficiency_bonus=2,
        skills={},
        background=bg_id,
        race=race_id,
        features=[feature_id],
        inventory=[item_id],
        classes=[],
        rollables={},
    )
    char_obj = GameObject(name="Hero", type="character", data=char.model_dump())

    objects = {feature_id: feature_obj, item_id: item_obj, bg_id: bg_obj, race_id: race_obj}

    monkeypatch.setattr(live_object, "GameObjectDAO", lambda: DummyDAO(objects))
    seq = iter([3, 2])
    monkeypatch.setattr(random, "randint", lambda a, b: next(seq))
    lc = cw.LiveCharacter(char_obj)
    assert lc.rollables["action"]["FeatRoll"].roll(lc) == 3
    assert lc.rollables["bonus_action"]["Sword"].roll(lc) == 2


def test_livecharacter_init_feature_ids(monkeypatch):
    feature_id = uuid4()

    class DummyDAO:
        def __init__(self):
            self.updated = None
        def update(self, obj):
            self.updated = obj
        def get_by_id(self, fid):
            assert fid == feature_id
            return DummyGameObject(id=fid, name="feat", type="feature", data={})

    monkeypatch.setattr(live_object, "GameObjectDAO", lambda: DummyDAO())
    monkeypatch.setattr(live_object, "hydrate", lambda g: SimpleNamespace(features=[feature_id]))
    monkeypatch.setattr(cw, "hydrate", lambda g: SimpleNamespace(modifiers=[]))

    char_obj = DummyGameObject(id=uuid4(), name="char", type="character", data={"features": [feature_id]})
    lc = cw.LiveCharacter(char_obj)
    assert len(lc.features) == 1


def test_grant_duplicates_and_missing_dao(monkeypatch):
    feature_id = uuid4()
    item_id = uuid4()

    feature_obj = GameObject(id=feature_id, name="feat", type="feature", data={"modifiers": []})
    item_obj = GameObject(id=item_id, name="item", type="item", data={"modifiers": [], "equipped": False})

    class DummyDAO:
        def __init__(self):
            self.objects = {feature_id: feature_obj, item_id: item_obj}
        def get_by_id(self, oid):
            return self.objects[oid]

    dummy = SimpleNamespace(
        dao=DummyDAO(),
        features=[],
        items=[],
        raw=SimpleNamespace(data={"features": [], "inventory": []}),
        process_count=0,
    )

    def process_change(self):
        dummy.process_count += 1

    monkeypatch.setattr(cw, "hydrate", lambda g: SimpleNamespace(**g.data))

    dummy.process_change = types.MethodType(process_change, dummy)
    dummy.grant = types.MethodType(cw.LiveCharacter.grant, dummy)

    # Grant without dao should be a no-op
    no_dao = SimpleNamespace()
    no_dao.grant = types.MethodType(cw.LiveCharacter.grant, no_dao)
    no_dao.grant(feature_id)

    # Grant feature twice to cover both branches
    dummy.grant(feature_id)
    assert dummy.raw.data["features"] == [feature_id]
    assert dummy.process_count == 1
    dummy.grant(feature_id)
    assert dummy.raw.data["features"] == [feature_id]
    assert dummy.process_count == 1

    # Grant item twice to cover inventory branch and unequipped modifiers
    dummy.grant(item_id)
    assert dummy.raw.data["inventory"] == [item_id]
    assert dummy.process_count == 2
    dummy.grant(item_id)
    assert dummy.raw.data["inventory"] == [item_id]
    assert dummy.process_count == 2


def test_apply_modifier_queues_grant():
    mod = SimpleNamespace(op="grant", value=uuid4())
    q = deque()
    seen = set()
    cw.LiveCharacter._apply_modifier(SimpleNamespace(), mod, q, seen)
    assert list(q) == [mod.value]


def test_apply_modifier_grant_without_instance_method(monkeypatch):
    captured = {}

    def fake_grant(self, value):
        captured["value"] = value

    monkeypatch.setattr(cw.LiveCharacter, "grant", fake_grant)
    dummy = SimpleNamespace(grant=None)
    mod = SimpleNamespace(op="grant", value=uuid4())
    cw.LiveCharacter._apply_modifier(dummy, mod)
    assert captured["value"] == mod.value
