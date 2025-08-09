from better5e.models.game_object import AnyGameObj
from pydantic import TypeAdapter
import sqlite3
from uuid import UUID
from pathlib import Path

TA = TypeAdapter(AnyGameObj)

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            
            cls._instances[cls] = super().__call__(*args, **kwargs)
        
        return cls._instances[cls]


class DAO(metaclass=SingletonMeta):
    db_name: Path = Path("better5e/db/better5e_v1.db")

    def __init__(self):
        self.conn = sqlite3.connect(self.db_name)
        self._startup()

    def _startup(self):
        sql_path = Path(__file__).with_name("startup.sql")
        with sql_path.open("r") as f:
            sql = f.read()

        self.conn.executescript(sql)
        self.conn.commit()

    def save(self, obj: AnyGameObj) -> None:
        payload = obj.model_dump_json()
        query = "INSERT INTO game_objects (id, kind, data)" \
        "           VALUES (?,?,?)" \
        "           ON CONFLICT(id) DO UPDATE SET" \
        "               kind = excluded.kind," \
        "               data = excluded.data"

        self.conn.execute(query, (str(obj.id), obj.kind, payload))
        self.conn.commit()

    def load_by_id(self, id: UUID) -> AnyGameObj | None:
        query = "SELECT data from game_objects WHERE id = ?"
        row = self.conn.execute(query, (str(id),)).fetchone()
        if not row:
            return None
        return TA.validate_json(row[0])
    
    def load_by_kind(self, kind: str) -> list[AnyGameObj]:
        query = "SELECT data from game_objects WHERE kind = ?"
        cur = self.conn.execute(query, (kind,))
        return [TA.validate_json(r[0]) for r in cur.fetchall()]
        
        

    
    

