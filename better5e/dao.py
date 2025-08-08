from __future__ import annotations

"""Data access objects for persisting game objects."""

import json
import sqlite3
from pathlib import Path
from typing import Optional
from uuid import UUID

from factory import create_game_object
from game_objects import GameObject


class GameObjectDAO:
    """Abstract DAO interface."""

    def load(self, obj_id: UUID) -> GameObject:  # pragma: no cover - interface
        raise NotImplementedError

    def save(self, obj: GameObject) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class FileDAO(GameObjectDAO):
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _path(self, obj: GameObject | UUID, obj_type: Optional[str] = None) -> Path:
        if isinstance(obj, GameObject):
            obj_type = obj.type
            obj_id = obj.uuid
        else:
            assert obj_type is not None
            obj_id = obj
        return self.base_path / obj_type / f"{obj_id}.json"

    def load(self, obj_id: UUID) -> GameObject:
        for type_dir in self.base_path.iterdir():
            candidate = type_dir / f"{obj_id}.json"
            if candidate.exists():
                data = json.loads(candidate.read_text())
                return create_game_object(data)
        raise FileNotFoundError(obj_id)

    def save(self, obj: GameObject) -> None:
        path = self._path(obj)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(obj.model_dump_json())


class SQLiteDAO(GameObjectDAO):
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS game_objects (uuid TEXT PRIMARY KEY, type TEXT, data TEXT)"
        )

    def load(self, obj_id: UUID) -> GameObject:
        cur = self.conn.execute(
            "SELECT type, data FROM game_objects WHERE uuid=?", (str(obj_id),)
        )
        row = cur.fetchone()
        if not row:
            raise KeyError(obj_id)
        data = json.loads(row[1])
        data["type"] = row[0]
        return create_game_object(data)

    def save(self, obj: GameObject) -> None:
        self.conn.execute(
            "REPLACE INTO game_objects (uuid, type, data) VALUES (?, ?, ?)",
            (str(obj.uuid), obj.type, obj.model_dump_json()),
        )
        self.conn.commit()
