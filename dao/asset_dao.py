from models.primitives import Asset
from models.types import *
from dao.connection import get_conn
import json

TABLE = "assets"

_TYPE_MAP: dict[str, type[Asset]] = {
    "feature": Feature,
    "spell": Spell,
    "item": Item,
    "class": Class,
    "subclass": Subclass,
    "resource": Resource
}

def insert(asset: Asset) -> None:
    with get_conn() as conn:
        conn.execute(
            f"""INSERT INTO {TABLE} (id, type, name, text, tags, data,
                                     created_by, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(asset.id),
                asset.type,
                asset.name,
                asset.text,
                json.dumps(asset.tags),
                json.dumps(asset.data or {}),
                asset.created_by,
                asset.created_at.isoformat(),
            ),
        )

def get(asset_id: str) -> Asset | None:
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT * FROM {TABLE} WHERE id = ?", (asset_id,)
        ).fetchone()
    return _row_to_asset(row) if row else None


def find_by_type(asset_type: str) -> list[Asset]:
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM {TABLE} WHERE type = ?", (asset_type,)
        ).fetchall()
    return [_row_to_asset(r) for r in rows]


def _row_to_asset(row) -> Asset:
    import json, datetime, uuid
    base_kwargs = {
        "id":         uuid.UUID(row["id"]),
        "type":       row["type"],
        "name":       row["name"],
        "text":       row["text"],
        "tags":       json.loads(row["tags"]),
        "data":       json.loads(row["data"]),
        "created_by": row["created_by"],
        "created_at": datetime.datetime.fromisoformat(row["created_at"]),
    }

    cls = _TYPE_MAP.get(row["type"], Asset)
    return cls(**base_kwargs)