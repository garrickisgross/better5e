import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from uuid import uuid4

import better5e.models.game_object as go
from better5e.models.enums import RechargeType, Op, ActionType
from better5e.dao import sqlite as sqlite_dao


def test_dao_round_trip(tmp_path):
    # Ensure we use a temporary database for isolation
    sqlite_dao.SingletonMeta._instances = {}
    sqlite_dao.DAO.db_name = tmp_path / "test.db"
    dao = sqlite_dao.DAO()

    feature = go.Feature(
        name="Darkvision",
        desc="See in the dark",
        uses_max=1,
        recharge=RechargeType.LONG_REST,
        modifiers=[go.Modifier(target="senses.darkvision", op=Op.SET, value=60)],
        actions=[go.Action(action_type=ActionType.ACTION)],
    )

    # save and reload by id
    dao.save(feature)
    loaded = dao.load_by_id(feature.id)
    assert loaded == feature

    # loading by kind returns the object
    objs = dao.load_by_kind("feature")
    assert feature in objs

    # unknown id returns None
    assert dao.load_by_id(uuid4()) is None
