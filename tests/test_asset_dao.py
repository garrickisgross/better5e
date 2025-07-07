import uuid
from datetime import datetime
from dao import asset_dao
from dao.init_db import init_db
from models.primitives import Asset
import pytest

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    from dao import connection
    test_db = tmp_path / "test.sqlite3"
    monkeypatch.setattr(connection, "DB_PATH", test_db)
    init_db()


def test_insert_and_get_asset():
    # Create a sample Asset with a type not in the _TYPE_MAP to use base Asset
    asset_id = uuid.uuid4()
    created_at = datetime.utcnow()
    asset = Asset(
        id=asset_id,
        type="spell",
        name="TestAsset",
        text="Sample text",
        tags=["tag1", "tag2"],
        data={"key": "value"},
        created_by="tester",
        created_at=created_at,
    )
    asset_dao.insert(asset)

    fetched = asset_dao.get(str(asset_id))
    assert fetched is not None
    assert fetched.id == asset.id
    assert fetched.type == asset.type
    assert fetched.name == asset.name
    assert fetched.text == asset.text
    assert fetched.tags == asset.tags
    assert fetched.data == asset.data
    assert fetched.created_by == asset.created_by
    # Compare ISO-formatted datetime strings
    assert fetched.created_at.isoformat().startswith(created_at.isoformat()[:19])


def test_find_by_type_returns_multiple():
    # Insert two assets of the same type
    now = datetime.utcnow()
    a1 = Asset(
        id=uuid.uuid4(),
        type="book",
        name="Book1",
        text="",
        tags=[],
        data={},
        created_by="u1",
        created_at=now,
    )
    a2 = Asset(
        id=uuid.uuid4(),
        type="book",
        name="Book2",
        text="",
        tags=[],
        data={},
        created_by="u2",
        created_at=now,
    )
    asset_dao.insert(a1)
    asset_dao.insert(a2)

    results = asset_dao.find_by_type("book")
    assert isinstance(results, list)
    ids = {r.id for r in results}
    assert ids == {a1.id, a2.id}