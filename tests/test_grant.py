from types import SimpleNamespace
from uuid import uuid4
import pytest

from wrappers import character_wrapper as cw


class DummyDAO:
    def __init__(self, objects):
        self.objects = objects
    def get_by_id(self, obj_id):
        return self.objects[obj_id]

class DummyChar:
    def __init__(self, dao):
        self.dao = dao
        self.raw = SimpleNamespace(data={"features": [], "inventory": []})
        self.features = []
        self.items = []
        self.set_calls = []
        self.process_calls = 0
    def set_data(self, target, value, op):
        self.set_calls.append((target, value, op))
    def process_change(self):
        self.process_calls += 1

def mod_set(val):
    return SimpleNamespace(target="stats.hp", op="set", value=val)

def mod_grant(ident):
    return SimpleNamespace(target="", op="grant", value=ident)


def test_grant_fifo_and_circular(monkeypatch):
    f1_id, f2_id, f3_id, item1_id, item2_id = [uuid4() for _ in range(5)]
    f1 = SimpleNamespace(
        id=f1_id,
        type="feature",
        modifiers=[
            mod_set(1),
            mod_grant(f2_id),
            mod_grant(f2_id),  # duplicate grant
            mod_grant(item1_id),
            mod_grant(item2_id),
        ],
    )
    f2 = SimpleNamespace(
        id=f2_id,
        type="feature",
        modifiers=[mod_set(2), mod_grant(f3_id)],
    )
    f3 = SimpleNamespace(
        id=f3_id,
        type="feature",
        modifiers=[mod_set(3), mod_grant(f1_id)],  # circular back to f1
    )
    item1 = SimpleNamespace(
        id=item1_id,
        type="item",
        modifiers=[mod_set(4)],
        equipped=True,
    )
    item2 = SimpleNamespace(
        id=item2_id,
        type="item",
        modifiers=[mod_set(5)],
        equipped=False,
    )

    dao = DummyDAO({
        f1_id: f1,
        f2_id: f2,
        f3_id: f3,
        item1_id: item1,
        item2_id: item2,
    })
    dummy = DummyChar(dao)
    monkeypatch.setattr(cw, "hydrate", lambda obj: obj)

    cw.LiveCharacter.grant(dummy, f1_id)

    assert dummy.features == [f1, f2, f3]
    assert dummy.items == [item1, item2]
    assert dummy.raw.data["features"] == [f1_id, f2_id, f3_id]
    assert dummy.raw.data["inventory"] == [item1_id, item2_id]

    values = [v for _, v, _ in dummy.set_calls]
    assert values == [1, 2, 4, 3]
    assert all(v != 5 for _, v, _ in dummy.set_calls)
    assert dummy.process_calls == 5


def test_grant_unknown_type_and_missing_dao(monkeypatch):
    obj_id = uuid4()
    unknown = SimpleNamespace(id=obj_id, type="mystery", modifiers=[mod_set(7)])
    dao = DummyDAO({obj_id: unknown})
    dummy = DummyChar(dao)
    monkeypatch.setattr(cw, "hydrate", lambda obj: obj)

    cw.LiveCharacter.grant(dummy, obj_id)

    assert dummy.set_calls == [("stats.hp", 7, "set")]
    assert dummy.features == []
    assert dummy.items == []
    assert dummy.process_calls == 0

    # absence of a DAO should be handled gracefully
    cw.LiveCharacter.grant(SimpleNamespace(), uuid4())


def test_grant_invalid_modifier(monkeypatch):
    bad_id = uuid4()
    bad_obj = SimpleNamespace(
        id=bad_id,
        type="feature",
        modifiers=[SimpleNamespace(target="", op="oops", value=0)],
    )
    dao = DummyDAO({bad_id: bad_obj})
    dummy = DummyChar(dao)
    monkeypatch.setattr(cw, "hydrate", lambda obj: obj)

    with pytest.raises(ValueError):
        cw.LiveCharacter.grant(dummy, bad_id)
