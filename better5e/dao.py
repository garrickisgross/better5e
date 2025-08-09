from uuid import UUID
from pydantic import TypeAdapter
from better5e.game_objects import GameObj
import sqlite3

TA_GO = TypeAdapter(GameObj)

db_name = "better5e_v1.db"

create_query = "CREATE TABLE IF NOT EXISTS game_objects (" \
"id          TEXT PRIMARY KEY," \
"kind        TEXT NOT NULL," \
"data        TEXT NOT NULL," \
"created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);"

index_on_kind = "CREATE INDEX IF NOT EXISTS idx_game_objects_kind ON game_objects(kind);"

save_query = "INSERT INTO game_objects (id, kind, data)" \
"VALUES (?, ?, ?)" \
"ON CONFLICT(id) DO UPDATE SET" \
"   kind = excluded.kind," \
"   data = excluded.data"

load_by_id = "SELECT data from game_objects WHERE id = ?"

load_by_kind = "SELECT data from game_objects WHERE kind = ? ORDER BY created_at DESC"




class GameDAO:
    """ Abstract interface for DAO """
    def load_by_id(self, id: UUID) -> GameObj:
        raise NotImplementedError
    
    def load_by_kind(self, kind: str) -> list[GameObj]:
        raise NotImplementedError

    def save(obj: GameObj) -> bool:
        raise NotImplementedError
    

class SQLite3DAO(GameDAO):

    def __init__(self):
        self.conn = sqlite3.connect(db_name)
        
        #execute startup scripts in order
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.conn.execute(create_query)
        self.conn.execute(index_on_kind)

        self.conn.commit()


    def load_by_id(self, id: UUID) -> GameObj:
        row = self.conn.execute(load_by_id, (str(id),)).fetchone()
        if not row:
            return ValueError("ID Invalid")
        return TA_GO.validate_json(row[0])
    
    def load_by_kind(self, kind: str) -> list[GameObj]:
        cursor = self.conn.execute(load_by_kind, (kind,))
        return [TA_GO.validate_json(r[0]) for r in cursor.fetchall()]

    def save(self, obj: GameObj) -> bool:
        payload = obj.model_dump_json()
        self.conn.execute(save_query, (str(obj.id), obj.kind, payload))
        self.conn.commit()