import sqlite3
import json
from uuid import uuid4
import pytest
from pydantic import ValidationError

from store import dao
from store.game_obj import GameObject


def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(dao, "DB", str(db_file))
    conn = dao.get_db_connection()
    conn.execute(
        "CREATE TABLE game_objects (id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL, data TEXT NOT NULL)"
    )
    conn.commit()
    conn.close()
    sqlite3.register_adapter(dict, lambda d: json.dumps(d))


def test_dao_operations(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    dao_obj = dao.GameObjectDAO()
    gobj = GameObject(name="obj", type="feature", data={})

    dao_obj.insert(gobj)
    with pytest.raises(ValueError):
        dao.insert_game_object(gobj)

    with pytest.raises(ValidationError):
        dao_obj.get_by_id(gobj.id)

    with pytest.raises(ValueError):
        dao_obj.get_by_id(uuid4())

    with pytest.raises(ValidationError):
        dao_obj.get_all_by_type("feature")

    gobj.name = "updated"
    dao_obj.update(gobj)

    fake = GameObject(id=uuid4(), name="fake", type="feature", data={})
    with pytest.raises(ValueError):
        dao_obj.update(fake)

    dao_obj.delete(gobj.id)
    assert dao.get_all_by_type("feature") == []
