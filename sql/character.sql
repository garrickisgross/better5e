PRAGMA foreign_keys = ON;

-- ============================================================
--  Core table: characters  (models.Character)
-- ============================================================
CREATE TABLE characters (
    id              INTEGER PRIMARY KEY,      -- uuid4().int ⇒ 64-bit INTEGER
    name            TEXT    NOT NULL,
    level           INTEGER NOT NULL,

    background_id   INTEGER,                  -- FK to a future "backgrounds" table
    abilities       TEXT    NOT NULL,         -- JSON  {"STR":15,"DEX":14,...}
    skills          TEXT,                     -- JSON  {"acrobatics":2,...}

    hit_points      INTEGER,
    max_hit_points  INTEGER,
    temp_hit_points INTEGER
);

-- ============================================================
--  Multiclass support  (character ⇔ classes)
--  level_per_class lets you record how many levels the PC has
--  in each class; omit it if you track that elsewhere.
-- ============================================================
CREATE TABLE character_classes (
    character_id    INTEGER NOT NULL
                         REFERENCES characters(id)
                         ON DELETE CASCADE,
    class_id        INTEGER NOT NULL
                         REFERENCES classes(id),

    level_in_class  INTEGER NOT NULL,         -- e.g. 3 Fighter / 2 Rogue

    PRIMARY KEY (character_id, class_id)
);

-- ============================================================
--  Subclasses chosen by the character
-- ============================================================
CREATE TABLE character_subclasses (
    character_id    INTEGER NOT NULL
                         REFERENCES characters(id)
                         ON DELETE CASCADE,
    subclass_id     INTEGER NOT NULL
                         REFERENCES subclasses(id),

    PRIMARY KEY (character_id, subclass_id)
);

-- ============================================================
--  Character ↔ Features  (feats, class features, item-granted, etc.)
-- ============================================================
CREATE TABLE character_features (
    character_id    INTEGER NOT NULL
                         REFERENCES characters(id)
                         ON DELETE CASCADE,
    feature_id      INTEGER NOT NULL
                         REFERENCES features(id),

    PRIMARY KEY (character_id, feature_id)
);

-- ============================================================
--  Character ↔ Items  (inventory)
--  `equipped` flag marks which items
