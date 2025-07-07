import uuid
import pytest
from models.primitives import Stat
from dao import stat_dao
from dao.init_db import init_db

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    # Override DB_PATH to a temporary file and initialize schema
    from dao import connection
    test_db = tmp_path / "test.sqlite3"
    monkeypatch.setattr(connection, "DB_PATH", test_db)
    init_db()


def test_get_by_key_none():
    assert stat_dao.get_by_key("nope") is None


def test_insert_and_get_by_key():
    stat = Stat(
        id=uuid.uuid4(),
        key="STR",
        name="Strength",
        description="Physical power",
        default=True,
    )
    stat_dao.insert(stat)
    fetched = stat_dao.get_by_key("STR")
    assert isinstance(fetched, Stat)
    assert fetched.key == stat.key
    assert fetched.name == stat.name
    assert fetched.description == stat.description
    assert fetched.default == stat.default


def test_all_stats():
    stat1 = Stat(
        key="DEX", name="Dexterity", description="", default=False
    )
    stat2 = Stat(
        key="INT", name="Intelligence", description="", default=True
    )
    stat_dao.insert(stat1)
    stat_dao.insert(stat2)

    all_stats = stat_dao.all_stats()
    assert isinstance(all_stats, dict)
    assert set(all_stats.keys()) >= {"DEX", "INT"}
    assert all_stats["INT"].default is True