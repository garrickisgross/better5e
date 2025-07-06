-- 1. Generic envelope  ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS assets (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,                -- 'stat', 'skill', …
    name        TEXT NOT NULL,
    text        TEXT DEFAULT '',
    tags        TEXT DEFAULT '[]',            -- JSON array
    data        TEXT DEFAULT '{}',            -- JSON blob
    created_by  TEXT,
    created_at  TEXT                          -- ISO date string
);

CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);

-- 2. Primitives  ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stats (
    id          TEXT PRIMARY KEY,
    key         TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS skills (
    id          TEXT PRIMARY KEY,
    key         TEXT UNIQUE NOT NULL,
    name        TEXT NOT NULL,
    governing_stat_key TEXT NOT NULL,
    FOREIGN KEY (governing_stat_key) REFERENCES stats(key)
);

