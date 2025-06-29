PRAGMA foreign_keys = ON;

-- ============================================================
--  Features  (represents models.Feature)
-- ============================================================
CREATE TABLE features (
    id                  INTEGER PRIMARY KEY,      -- uuid4().int → 64-bit INTEGER*
    name                TEXT    NOT NULL,

    prerequisites       TEXT,                     -- JSON Object[str, Any] (e.g. {"level": 3, "class": "fighter"})
    prerequisites_text  TEXT,                     -- human-readable text for prerequisites
    feature_type        TEXT    NOT NULL,         -- “class feature”, “feat”, “racial”, …
    description         TEXT,
    action_type         TEXT,                     -- “action”, “bonus action”, “reaction”, …
    uses                INTEGER,                  -- times per rest (NULL = unlimited)
    recharge            TEXT,                     -- “short rest”, “long rest”, etc.

    -- JSON blobs for one-to-many lists
    granted_features    TEXT,                     -- JSON array[int]
    granted_spells      TEXT,                     -- JSON array[int]
    granted_items       TEXT,                     -- JSON array[int]
    modifiers           TEXT,                     -- JSON array[Modifier]
    rollable            TEXT,                     -- JSON for Rollable (or plain string)
    options             TEXT,                     -- JSON array[int] (sub-feature IDs)
    choice_count        INTEGER   DEFAULT 1
);
