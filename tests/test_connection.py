import sqlite3
import pytest
from dao import connection
from dao.connection import get_conn

def test_get_conn_creates_db(tmp_path, monkeypatch):
    # Override the database path to a temporary file
    db_file = tmp_path / "test.sqlite3"
    monkeypatch.setattr(connection, "DB_PATH", db_file)

    # Use the connection context manager
    with get_conn() as conn:
        # Should be a sqlite3.Connection instance
        assert isinstance(conn, sqlite3.Connection)
        # Row factory should be sqlite3.Row for dict-like rows
        assert conn.row_factory == sqlite3.Row

        # Foreign keys pragma should be enabled (value 1)
        cursor = conn.execute("PRAGMA foreign_keys")
        fk = cursor.fetchone()[0]
        assert fk == 1

    # The database file should have been created
    assert db_file.exists()