import pytest
from dao import init_db
from dao.connection import get_conn

@pytest.fixture(autouse=True)
def init_db_temp(tmp_path, monkeypatch):
    # Override the database path for testing
    from dao import connection
    test_db = tmp_path / "test.sqlite3"
    monkeypatch.setattr(connection, "DB_PATH", test_db)
    # Initialize the database schema
    init_db.init_db()
    return test_db


def test_init_db_runs_and_creates_tables(init_db_temp):
    # Should print a success message
    # (capturing stdout is optional if init_db prints)
    # Verify that the 'assets' table exists
    with get_conn() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='assets'"
        )
        assert cursor.fetchone() is not None