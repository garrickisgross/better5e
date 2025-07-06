from models.primitives import Stat
from dao.connection import get_conn

TABLE = "stats"

def insert(stat: Stat) -> None:
    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO {TABLE} (id, key, name, description) "
            "VALUES (?, ?, ?, ?)",
            (str(stat.id), stat.key, stat.name, stat.description),
        )

def get_by_key(key: str) -> Stat | None:
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT * FROM {TABLE} WHERE key = ?", (key,)
        ).fetchone()
    return Stat(**row) if row else None


def all_stats() -> dict[str, Stat]:
    with get_conn() as conn:
        rows = conn.execute(f"SELECT * FROM {TABLE}").fetchall()
    return {row["key"]: Stat(**row) for row in rows}
