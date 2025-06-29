PRAGMA foreign_keys = ON;

-- ============================================================
--  Spells  (models.Spell)
-- ============================================================
CREATE TABLE spells (
    id                  INTEGER PRIMARY KEY,          -- uuid4().int → 64-bit INTEGER
    name                TEXT    NOT NULL,
    level               INTEGER NOT NULL,             -- 0 = cantrip
    school              TEXT    NOT NULL,             -- "evocation", "illusion", …

    casting_time        TEXT    NOT NULL,             -- "1 action", "1 bonus action", …
    "range"             TEXT    NOT NULL,             -- quoted because RANGE is keyword
    components          TEXT    NOT NULL,             -- JSON array ["V","S","M"]
    duration            TEXT    NOT NULL,             -- "1 minute", "instantaneous", …

    description         TEXT,
    higher_level_effects TEXT,                        -- JSON Modifier object
    material_components TEXT,                         -- free-form, e.g. “a pinch of …”
    ritual              INTEGER DEFAULT 0,            -- 1 = can be cast as ritual

    damage              TEXT,                         -- JSON Rollable object (or NULL)
    area_of_effect      TEXT,                         -- e.g. "20-foot radius"
    saving_throw        TEXT                          -- "Dexterity", "Constitution", …
);
