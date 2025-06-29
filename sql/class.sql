PRAGMA foreign_keys = ON;

-- ============================================================
--  Classes  (models.Class)
-- ============================================================
CREATE TABLE classes (
    id                      INTEGER PRIMARY KEY,          -- uuid4().int ⇒ 64-bit INTEGER
    name                    TEXT    NOT NULL,
    description             TEXT,

    hit_die                 INTEGER NOT NULL,             -- e.g. 10 for Fighter
    spellcasting_ability    TEXT,                         -- "INT", "CHA", etc.
    spellcasting_type       TEXT,                         -- "prepared", "known", NULL

    spells_known_by_level   TEXT,                         -- JSON {level : [spellIds]}
    allowed_spells          TEXT,                         -- JSON [spellIds]
    spell_slots_by_level    TEXT,                         -- JSON {level : {spellLvl : n}}
    features_by_level       TEXT,                         -- JSON {level : [featureIds]}

    subclass_choice_level   INTEGER,                      -- when the subclass is chosen
    subclass_options        TEXT                          -- JSON [subclassIds]
);

-- ============================================================
--  Subclasses  (models.Subclass)
-- ============================================================
CREATE TABLE subclasses (
    id                  INTEGER PRIMARY KEY,
    name                TEXT    NOT NULL,
    parent_class_id     INTEGER NOT NULL
                                REFERENCES classes(id)
                                ON DELETE CASCADE,

    description         TEXT,
    features_by_level   TEXT,                             -- JSON {level : [featureIds]}
    granted_spells      TEXT                              -- JSON [spellIds]
);
