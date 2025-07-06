# dao/skill_dao.py
from models.primitives import Skill
from dao import stat_dao
from dao.connection import get_conn

TABLE = "skills"

def insert(skill: Skill) -> None:
    # FK guard at Python level — friendlier error than raw SQL
    if stat_dao.get_by_key(skill.governing_stat_key) is None:
        raise ValueError(f"Unknown Stat {skill.governing_stat_key}")

    with get_conn() as conn:
        conn.execute(
            f"INSERT INTO {TABLE} (id, key, name, governing_stat_key, is_default) "
            "VALUES (?, ?, ?, ?, ?)",
            (str(skill.id), skill.key, skill.name, skill.governing_stat_key, skill.default),
        )

def get_by_key(key: str) -> Skill | None:
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT * FROM {TABLE} WHERE key = ?", (key,)
        ).fetchone()
    return Skill(**row) if row else None

def all_stats() -> dict[str, Skill]:
    with get_conn() as conn:
        rows = conn.execute(f"SELECT * FROM {TABLE}").fetchall()
    return {row["key"]: Skill(**row) for row in rows}