import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Type, TypeVar
from pathlib import Path

from pydantic import BaseModel

DATABASE_FILE = Path("better5e.db")

def _dict_factory(cursor, row):
    """Convert rows to dictionaries."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@contextmanager
def get_db_connection():
    """Context manager to handle database connections."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = _dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        
        conn.close()


T = TypeVar("T", bound=BaseModel)

class BaseRepo:
    TABLE: str
    MODEL: Type[T]
    JSON_COLS: List[str] = []

    @classmethod
    def _encode(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: json.dumps(v) if k in cls.JSON_COLS and v is not None else v
                for k, v in data.items()}

    @classmethod
    def _decode(cls, row: Dict[str, Any]) -> T:
        for col in cls.JSON_COLS:
            if row.get(col) is not None:
                row[col] = json.loads(row[col])
        return cls.MODEL(**row)

    # ---------- CRUD ----------
    @classmethod
    def create(cls, obj: T) -> int:
        data = cls._encode(obj.model_dump(exclude_none=True))
        cols, vals = zip(*data.items())
        with get_db_connection() as db:
            db.execute(f"INSERT INTO {cls.TABLE} ({','.join(cols)})"
                       f" VALUES ({','.join('?'*len(vals))})", vals)
            return db.execute("SELECT last_insert_rowid()").fetchone()["last_insert_rowid()"]

    @classmethod
    def get(cls, item_id: int) -> T:
        with get_db_connection() as db:
            row = db.execute(f"SELECT * FROM {cls.TABLE} WHERE id = ?", (item_id,)).fetchone()
            if not row:
                raise KeyError(f"{cls.TABLE[:-1].capitalize()} {item_id} not found")
            return cls._decode(row)

    @classmethod
    def list_all(cls) -> List[T]:
        with get_db_connection() as db:
            rows = db.execute(f"SELECT * FROM {cls.TABLE}").fetchall()
            return [cls._decode(r) for r in rows]

    @classmethod
    def update(cls, item_id: int, **updates):
        data = cls._encode(updates)
        sets, vals = zip(*data.items()) if data else ([], [])
        if sets:
            with get_db_connection() as db:
                db.execute(f"UPDATE {cls.TABLE} SET "
                           f"{', '.join(f'{c}=?' for c in sets)} WHERE id = ?",
                           (*vals, item_id))

    @classmethod
    def delete(cls, item_id: int):
        with get_db_connection() as db:
            db.execute(f"DELETE FROM {cls.TABLE} WHERE id = ?", (item_id,))