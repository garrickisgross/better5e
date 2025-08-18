import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import better5e.models.game_object as go
from better5e.models.enums import RechargeType, Op, ActionType
from pydantic import TypeAdapter


def test_feature_serialization_round_trip():
    feature = go.Feature(
        name="Darkvision",
        desc="See in the dark",
        uses_max=1,
        recharge=RechargeType.LONG_REST,
        modifiers=[go.Modifier(target="senses.darkvision", op=Op.SET, value=60)],
        actions=[go.Action(action_type=ActionType.ACTION)],
    )
    adapter = TypeAdapter(go.AnyGameObj)
    parsed = adapter.validate_json(feature.model_dump_json())
    assert parsed == feature


def test_default_lists_are_independent():
    f1 = go.Feature(name="F1", desc="d1")
    f2 = go.Feature(name="F2", desc="d2")
    f1.actions.append(go.Action(action_type=ActionType.ACTION))
    assert f2.actions == []


def test_enum_values():
    assert RechargeType.SHORT_REST.value == "short_rest"
    assert Op.MUL.value == "mul"
    assert ActionType.DAMAGE.value == "damage"
