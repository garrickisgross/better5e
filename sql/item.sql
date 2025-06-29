-- ------------------------------------------------------------
--  Enable FK enforcement (run once per connection)
-- ------------------------------------------------------------
PRAGMA foreign_keys = ON;

-- ============================================================
--  Base table: items  (represents Item)
-- ============================================================
CREATE TABLE items (
    id                  INTEGER PRIMARY KEY,                -- uuid4().int fits in 64-bit INTEGER
    name                TEXT        NOT NULL,
    item_type           TEXT        NOT NULL,               -- "weapon", "armor", "consumable", "tool"
    action_type         TEXT,
    rarity              TEXT,                               -- "common", "rare", etc.
    description         TEXT,
    weight              REAL,
    value               REAL,
    requires_attunement INTEGER     DEFAULT 0,              -- 0 = false, 1 = true

    -- JSON blobs for lists of IDs
    granted_features    TEXT,                               -- JSON array[int]
    granted_spells      TEXT,                               -- JSON array[int]
    granted_items       TEXT                                -- JSON array[int]
);

-- ============================================================
--  Weapons  (extra fields for class Weapon)
-- ============================================================
CREATE TABLE weapons (
    item_id        INTEGER PRIMARY KEY
                              REFERENCES items(id) ON DELETE CASCADE,

    attack_type    TEXT        NOT NULL,                    -- e.g. "melee weapon"
    damage         TEXT        NOT NULL,                    -- Rollable string, e.g. "1d8+2"
    "range"        TEXT,                                    -- quoted because RANGE is a keyword
    attack         TEXT        NOT NULL,                    -- Rollable string or formula
    damage_type    TEXT        NOT NULL,                    -- "slashing", "fire", etc.
    magic_bonus    INTEGER     DEFAULT 0,
    modifiers      TEXT                                        -- JSON array[Modifier]
);

-- ============================================================
--  Armors  (class Armor)
-- ============================================================
CREATE TABLE armors (
    item_id        INTEGER PRIMARY KEY
                              REFERENCES items(id) ON DELETE CASCADE,

    base_ac        INTEGER     NOT NULL,
    max_dex_bonus  INTEGER
);

-- ============================================================
--  Consumables  (class Consumable)
-- ============================================================
CREATE TABLE consumables (
    item_id        INTEGER PRIMARY KEY
                              REFERENCES items(id) ON DELETE CASCADE,

    rollable       TEXT,                                    -- JSON / string
    duration       INTEGER,                                 -- in rounds, minutes, etc.
    uses           INTEGER     DEFAULT 1
);

-- ============================================================
--  Tools  (class Tool)
-- ============================================================
CREATE TABLE tools (
    item_id                INTEGER PRIMARY KEY
                                    REFERENCES items(id) ON DELETE CASCADE,

    tool_type              TEXT        NOT NULL,
    proficiency_required   INTEGER     DEFAULT 0            -- 0 = false, 1 = true
);
