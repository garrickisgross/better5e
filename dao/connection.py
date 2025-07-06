from contextlib import contextmanager
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "dnd.sqlite3"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row           # → dict-like rows
    conn.execute("PRAGMA foreign_keys = ON") # FK enforcement
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
