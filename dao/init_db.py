# dao/init_db.py
from pathlib import Path
from dao.connection import get_conn



def init_db() -> None:
    """
    Create all tables and pragma settings declared in schema.sql.
    Safe to run multiple times (uses IF NOT EXISTS in the DDL).
    """
    SCHEMA_PATH = Path(__file__).with_name("schema.sql")
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError("schema.sql not found next to init_db.py")

    ddl = SCHEMA_PATH.read_text()

    with get_conn() as conn:
        # Enable FK checks for the current session
        conn.execute("PRAGMA foreign_keys = ON")
        # Execute the entire DDL script (CREATE TABLE …)
        conn.executescript(ddl)

    print("SQLite schema initialized ✔")
