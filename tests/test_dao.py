import sqlite3
from uuid import uuid4
import pytest
from store.game_obj import GameObject
import store.dao as dao


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(dao, "DB", str(db_path))
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE game_objects (id TEXT PRIMARY KEY, name TEXT, type TEXT, data TEXT)"
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(dao, "hydrate", lambda g: g)
    return dao.GameObjectDAO()


def test_dao_crud_operations(temp_db):
    dao_obj = temp_db
    obj = GameObject(id=uuid4(), name="n", type="feature", data={"x": 1})
    dao_obj.insert(obj)
    assert dao.get_game_object_by_id(obj.id).name == "n"
    all_objs = dao_obj.get_all_by_type("feature")
    assert all_objs and all_objs[0].id == obj.id
    obj.name = "new"
    dao_obj.update(obj)
    assert dao_obj.get_by_id(obj.id).name == "new"
    with pytest.raises(ValueError):
        dao_obj.insert(obj)
    missing = GameObject(id=uuid4(), name="m", type="feature", data={})
    with pytest.raises(ValueError):
        dao_obj.update(missing)
    dao_obj.delete(obj.id)
    assert dao_obj.get_all_by_type("feature") == []
    with pytest.raises(ValueError):
        dao_obj.get_by_id(obj.id)
