import uuid
import pytest
from better5e.dao import FileDAO, SQLiteDAO
from better5e.game_objects import Item, GameObject


def test_file_dao(tmp_path):
    dao = FileDAO(tmp_path)
    obj = Item(name="Sword")
    path1 = dao._path(obj)
    path2 = dao._path(obj.uuid, obj.type)
    assert path1 == path2

    dao.save(obj)
    loaded = dao.load(obj.uuid)
    assert loaded == obj

    with pytest.raises(FileNotFoundError):
        dao.load(uuid.uuid4())


def test_sqlite_dao(tmp_path):
    dao = SQLiteDAO(tmp_path / "db.sqlite")
    obj = Item(name="Sword")
    dao.save(obj)
    loaded = dao.load(obj.uuid)
    assert loaded == obj

    with pytest.raises(KeyError):
        dao.load(uuid.uuid4())
