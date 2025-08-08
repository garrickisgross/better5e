import json
from uuid import UUID, uuid4

import pytest
from hypothesis import given, strategies as st

from better5e.dao import GameObjectDAO
from better5e.game_objects import Item
from better5e.modifiers import ModifierOperation
from better5e.wizard import GameObjectWizard, WizardError, validate_dice


class DictDAO(GameObjectDAO):
    def __init__(self):
        self.storage = {}

    def load(self, obj_id: UUID):
        return self.storage[obj_id]

    def save(self, obj):
        self.storage[obj.uuid] = obj


def new_wiz():
    return GameObjectWizard(DictDAO())


def spec_path(name: str) -> str:
    return f"tests/golden/{name}.json"


def test_form_spec_golden():
    wiz = new_wiz()
    for obj_type in ["feature", "item", "spell", "race", "background", "class"]:
        spec = wiz.get_form_spec(obj_type)
        with open(spec_path(obj_type)) as f:
            assert spec == json.load(f)


def test_modifiers_validation_including_grant_uuid_coercion():
    wiz = new_wiz()
    sid = wiz.start("feature")
    # core
    wiz.apply(sid, {"name": "Bless"}, revision=0)
    # type step with nothing
    wiz.apply(sid, {}, revision=1)
    gid = uuid4()
    resp = wiz.apply(
        sid,
        {"modifiers": [{"target": "stats.str", "operation": "grant", "value": str(gid)}]},
        revision=2,
    )
    session = wiz._sessions[sid]
    assert session.modifiers[0]["value"] == [str(gid)]
    wiz.apply(sid, {"grants": []}, revision=3)
    obj = wiz.finalize(sid, save=False)
    mod = obj["model"]["modifiers"][0]
    assert mod["operation"] == ModifierOperation.GRANT.value
    assert mod["value"] == [str(gid)]


@given(
    count=st.integers(min_value=1, max_value=5),
    sides=st.sampled_from([4, 6, 8, 10, 12, 20, 100]),
    mod=st.integers(min_value=-5, max_value=5),
)
def test_dice_validation_property_based(count, sides, mod):
    expr = f"{count}d{sides}{mod:+d}" if mod else f"{count}d{sides}"
    validate_dice(expr)


def test_finalize_materializes_correct_subclass_and_persists():
    wiz = new_wiz()
    sid_feat = wiz.start("feature")
    wiz.apply(sid_feat, {"name": "Darkvision"}, revision=0)
    wiz.apply(sid_feat, {}, revision=1)
    wiz.apply(sid_feat, {"modifiers": []}, revision=2)
    wiz.apply(sid_feat, {"grants": []}, revision=3)
    grant_obj = wiz.finalize(sid_feat, save=True)

    sid = wiz.start("item")
    wiz.apply(sid, {"name": "Axe"}, revision=0)
    wiz.apply(
        sid,
        {"category": "weapon", "damage": "1d8", "damage_type": "slashing"},
        revision=1,
    )
    wiz.apply(sid, {"modifiers": []}, revision=2)
    wiz.apply(sid, {"grants": [grant_obj["uuid"]]}, revision=3)
    preview = wiz.preview(sid)
    assert preview["modifier_count"] == 0
    result = wiz.finalize(sid, save=True)
    dao = wiz.dao
    loaded = dao.load(UUID(result["uuid"]))
    assert isinstance(loaded, Item)
    assert loaded.data["damage"] == "1d8"


def test_edit_existing_roundtrip_update():
    wiz = new_wiz()
    sid = wiz.start("item")
    wiz.apply(sid, {"name": "Sword"}, revision=0)
    wiz.apply(sid, {"category": "weapon", "damage": "1d8", "damage_type": "slashing"}, revision=1)
    wiz.apply(sid, {"modifiers": []}, revision=2)
    wiz.apply(sid, {"grants": []}, revision=3)
    obj = wiz.finalize(sid, save=True)
    oid = UUID(obj["uuid"])
    # load existing and change name
    sid2 = wiz.load_existing(oid)
    wiz.apply(sid2, {"name": "Great Sword"}, revision=0)
    wiz.apply(sid2, {"category": "weapon", "damage": "1d8", "damage_type": "slashing"}, revision=1)
    wiz.apply(sid2, {"modifiers": []}, revision=2)
    wiz.apply(sid2, {"grants": []}, revision=3)
    final = wiz.finalize(sid2, save=True)
    assert final["uuid"] == obj["uuid"]
    assert wiz.dao.load(oid).name == "Great Sword"


def test_idempotent_apply_does_not_duplicate_entries():
    wiz = new_wiz()
    sid = wiz.start("item")
    resp1 = wiz.apply(sid, {"name": "Hammer"}, revision=0)
    resp2 = wiz.apply(sid, {"name": "Hammer"}, revision=0)
    assert resp1 == resp2
    assert wiz._sessions[sid].step_index == 1
    wiz.apply(sid, {"category": "weapon", "damage": "1d4", "damage_type": "bludgeoning"}, revision=1)
    wiz.apply(sid, {"modifiers": []}, revision=2)
    wiz.apply(sid, {"grants": []}, revision=3)
    wiz.finalize(sid, save=False)


def test_validation_errors():
    wiz = new_wiz()
    sid = wiz.start("item")
    with pytest.raises(WizardError):
        wiz.apply(sid, {"unknown": 1}, revision=0)
    with pytest.raises(WizardError):
        wiz.apply(sid, {})
    with pytest.raises(WizardError):
        wiz.apply(sid, {}, revision=0)
    wiz.apply(sid, {"name": "Bow"}, revision=0)
    with pytest.raises(WizardError):
        wiz.apply(sid, {"category": "weapon"}, revision=1)  # missing damage
    with pytest.raises(WizardError):
        wiz.apply(sid, {"category": "weapon", "damage": "1d3", "damage_type": "piercing"}, revision=1)
    with pytest.raises(WizardError):
        wiz.apply(sid, {"category": "weapon", "damage": "1d8"}, revision=1)
    wiz.apply(sid, {"category": "weapon", "damage": "1d8", "damage_type": "piercing"}, revision=1)
    with pytest.raises(WizardError):
        wiz.apply(sid, {"modifiers": [{"target": "x", "operation": "add", "value": 1, "extra": 1}]}, revision=2)
    with pytest.raises(WizardError):
        wiz.apply(sid, {"modifiers": [{"target": "x", "operation": "bad", "value": 1}]}, revision=2)
    wiz.apply(sid, {"modifiers": []}, revision=2)
    with pytest.raises(WizardError):
        wiz.apply(sid, {"grants": ["not-a-uuid"]}, revision=3)
    good = str(uuid4())
    wiz.apply(sid, {"grants": [good]}, revision=3)
    with pytest.raises(WizardError):
        wiz.apply(sid, {}, revision=5)  # revision mismatch
    sid_fail = wiz.start("item")
    with pytest.raises(WizardError):
        wiz.finalize(sid_fail, save=False)

    # feature uses.max negative
    sid2 = wiz.start("feature")
    wiz.apply(sid2, {"name": "Rage"}, revision=0)
    with pytest.raises(WizardError):
        wiz.apply(sid2, {"uses.max": -1}, revision=1)
    wiz.preview(sid2)

    # spell invalid components
    sid3 = wiz.start("spell")
    wiz.apply(sid3, {"name": "Fire"}, revision=0)
    with pytest.raises(WizardError):
        wiz.apply(sid3, {"level": 1, "components": ["X"]}, revision=1)
    with pytest.raises(WizardError):
        wiz.apply(sid3, {"level": 10}, revision=1)
    wiz.cancel(sid3)

    sid5 = wiz.start("spell")
    wiz.apply(sid5, {"name": "Zap"}, revision=0)
    with pytest.raises(WizardError):
        wiz.apply(sid5, {"level": 0, "damage_type": "fire"}, revision=1)
    wiz.cancel(sid5)

    sid4 = wiz.start("spell")
    wiz.apply(sid4, {"name": "Bolt"}, revision=0)
    wiz.apply(sid4, {"level": 0, "damage": "1d8", "damage_type": "fire"}, revision=1)
    wiz.preview(sid4)

    err = WizardError("oops", "bad", field="x", detail={"a": 1})
    assert err.to_dict()["field"] == "x"

    # start with template
    tmpl = {
        "core": {"name": "Tmp"},
        "data": {"category": "gear"},
        "modifiers": [{"target": "x", "operation": "add", "value": 1}],
        "grants": [good],
    }
    sid_t = wiz.start("item", template=tmpl)
    assert wiz.preview(sid_t)["name"] == "Tmp"

    # invalid dice syntax
    with pytest.raises(WizardError):
        validate_dice("bad")
