CREATE TABLE IF NOT EXISTS game_objects (
    id      TEXT PRIMARY KEY,
    kind    TEXT NOT NULL,
    data    TEXT NOT NULL,
    created_at TEXT DEFAULT (CURRENT_TIMESTAMP)
);

CREATE INDEX IF NOT EXISTS idx_game_objects_kind ON game_objects(kind);


