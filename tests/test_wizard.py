import pytest
from uuid import UUID, uuid4
from pathlib import Path

from better5e.dao import FileDAO
from better5e.wizard import GameObjectWizard
from better5e.wizard import build_modifier
from better5e.modifiers import ModifierOperation
from better5e.game_objects import Feature, Item


def make_wizard(tmp_path: Path) -> GameObjectWizard:
    return GameObjectWizard(FileDAO(tmp_path))


def test_form_spec_contains_core_and_type_specific_fields(tmp_path):
    wiz = make_wizard(tmp_path)
    spec = wiz.get_form_spec("feature")
    core = spec["steps"][0]["fields"]
    ts = spec["steps"][1]["fields"]
    assert any(f["key"] == "name" for f in core)
    assert any(f["key"] == "data.description" for f in ts)


def test_build_feature_with_modifiers_and_grants_roundtrip_save(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("feature")
    wiz.apply(sid, {"name": "Sneak", "type": "feature"})
    wiz.apply(
        sid,
        {
            "data": {
                "description": "Sneaky",
                "activation": "action",
                "uses": {"max": 1, "recharge": "short_rest"},
            }
        },
    )
    grant_id = uuid4()
    wiz.apply(
        sid,
        {
            "modifiers": [
                {"target": "stats.dexterity", "operation": "add", "value": 2},
                {"target": "stats.strength", "operation": "grant", "value": str(grant_id)},
            ]
        },
    )
    wiz.apply(sid, {"grants": []})
    preview = wiz.preview(sid)
    assert preview["modifiers"] == 2
    result = wiz.finalize(sid, save=True)
    dao = wiz.dao
    loaded = dao.load(UUID(result["uuid"]))
    assert isinstance(loaded, Feature)
    assert loaded.name == "Sneak"


def test_spell_level_validation_and_dice_validation(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("spell")
    wiz.apply(sid, {"name": "Firebolt", "type": "spell"})
    with pytest.raises(ValueError):
        wiz.apply(sid, {"data": {"level": 10}})
    with pytest.raises(ValueError):
        wiz.apply(
            sid,
            {
                "data": {
                    "level": 1,
                    "school": "evocation",
                    "casting_time": "1 action",
                    "range": "60 ft",
                    "duration": "instant", "components": [],
                    "attack_save": "none", "damage": "bad"
                }
            },
        )


def test_finalize_materializes_correct_subclass_and_persists(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("item")
    wiz.apply(sid, {"name": "Sword", "type": "item"})
    wiz.apply(
        sid,
        {
            "data": {
                "category": "weapon",
                "damage": "1d6",
                "damage_type": "slashing",
            }
        },
    )
    wiz.apply(sid, {"modifiers": []})
    wiz.apply(sid, {"grants": []})
    wiz.apply(sid, {})  # review step
    res = wiz.preview(sid)
    assert res["damage"] == "1d6"
    fin = wiz.finalize(sid)
    loaded = wiz.dao.load(UUID(fin["uuid"]))
    assert isinstance(loaded, Item)


def test_preview_returns_expected_summary(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("spell")
    wiz.apply(sid, {"name": "Magic", "type": "spell"})
    wiz.apply(
        sid,
        {
            "data": {
                "level": 1,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "30 ft",
                "duration": "instant",
                "components": [],
                "attack_save": "none",
            }
        },
    )
    mod = {"target": "roll", "operation": "add", "value": 1}
    grant = str(uuid4())
    wiz.apply(sid, {"modifiers": [mod]})
    wiz.apply(sid, {"grants": [grant]})
    prev = wiz.preview(sid)
    assert prev["level"] == 1
    assert prev["school"] == "evocation"
    assert prev["modifiers"] == 1
    assert prev["grants"] == [grant]
    wiz.cancel(sid)


def test_apply_core_validation(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("feature")
    with pytest.raises(ValueError):
        wiz.apply(sid, {})
    with pytest.raises(ValueError):
        wiz.apply(sid, {"name": "A", "type": "item"})


def test_type_data_validation_errors(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("feature")
    wiz.apply(sid, {"name": "Feat", "type": "feature"})
    with pytest.raises(ValueError):
        wiz.apply(sid, {"data": {"uses": {"max": -1}}})
    sid2 = wiz.start("spell")
    wiz.apply(sid2, {"name": "Bolt", "type": "spell"})
    with pytest.raises(ValueError):
        wiz.apply(sid2, {"data": {"level": 1, "damage_type": "fire"}})


def test_start_template_and_finalize_without_save(tmp_path):
    ids = [str(uuid4()), str(uuid4())]
    template = {"name": "Temp", "modifiers": [{"target": "roll", "operation": "grant", "value": ids}]}
    wiz = make_wizard(tmp_path)
    sid = wiz.start("feature", template=template)
    prev = wiz.preview(sid)
    assert prev["name"] == "Temp"
    res = wiz.finalize(sid, save=False)
    path = tmp_path / "feature" / f"{res['uuid']}.json"
    assert not path.exists()


def test_preview_other_types_and_item_highlight(tmp_path):
    wiz = make_wizard(tmp_path)
    # item preview
    sid_item = wiz.start("item")
    wiz.apply(sid_item, {"name": "Hammer", "type": "item"})
    wiz.apply(sid_item, {"data": {"category": "tool"}})
    wiz.apply(sid_item, {"modifiers": []})
    wiz.apply(sid_item, {"grants": []})
    wiz.apply(sid_item, {})  # review branch
    prev_item = wiz.preview(sid_item)
    assert prev_item["category"] == "tool"
    # race preview to hit default branch
    sid_race = wiz.start("race")
    wiz.apply(sid_race, {"name": "Elf", "type": "race"})
    wiz.apply(sid_race, {"data": {"size": "medium", "speed": 30, "languages": [], "traits": []}})
    wiz.apply(sid_race, {"modifiers": []})
    wiz.apply(sid_race, {"grants": []})
    wiz.apply(sid_race, {})
    prev_race = wiz.preview(sid_race)
    assert prev_race["name"] == "Elf"
    assert "category" not in prev_race and "level" not in prev_race


def test_build_modifier_multi_grant():
    ids = [str(uuid4()), str(uuid4())]
    mod = build_modifier({"target": "roll", "operation": "grant", "value": ids})
    assert isinstance(mod.value, list) and len(mod.value) == 2


def test_finalize_incomplete_session(tmp_path):
    wiz = make_wizard(tmp_path)
    sid = wiz.start("item")
    with pytest.raises(ValueError):
        wiz.finalize(sid)
