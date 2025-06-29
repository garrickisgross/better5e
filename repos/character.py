# character_repo.py  ----------------------------------------------------------
from typing import List, Any
import json

from models.character import Character
from database import BaseRepo, get_db_connection


class CharacterRepo(BaseRepo):
    TABLE = "characters"
    MODEL = Character
    JSON_COLS = ["abilities", "skills"]

    # ------------------------------------------------------------------ CREATE
    @classmethod
    def create(cls, character: Character) -> int:
        """
        Insert the Character row, then populate 4 junction tables:
        character_classes, character_subclasses, character_features, character_items
        (items uses the 'equipped' flag instead of a second table).
        """
        data = cls._encode(character.model_dump(exclude_none=True))

        # pull list fields out of the dict before INSERT
        class_ids       = data.pop("class_id",      [])
        subclass_ids    = data.pop("subclass_id",   [])
        feature_ids     = data.pop("features",      [])
        item_ids        = data.pop("items",         [])
        equipped_items  = set(data.pop("equipped_items", []))

        cols, vals = zip(*data.items())             # safe: at least `name`, `level`

        with get_db_connection() as db:
            db.execute(f"INSERT INTO {cls.TABLE} ({','.join(cols)}) "
                       f"VALUES ({','.join('?' * len(vals))})", vals)
            char_id = db.execute("SELECT last_insert_rowid()").fetchone()["last_insert_rowid()"]

            # --- junction inserts
            db.executemany(
                "INSERT INTO character_classes (character_id, class_id, level_in_class) VALUES (?, ?, ?)",
                [(char_id, cid, 1) for cid in class_ids])                      # default 1 level
            db.executemany(
                "INSERT INTO character_subclasses (character_id, subclass_id) VALUES (?, ?)",
                [(char_id, sid) for sid in subclass_ids])
            db.executemany(
                "INSERT INTO character_features (character_id, feature_id) VALUES (?, ?)",
                [(char_id, fid) for fid in feature_ids])
            db.executemany(
                "INSERT INTO character_items (character_id, item_id, equipped) VALUES (?, ?, ?)",
                [(char_id, iid, 1 if iid in equipped_items else 0) for iid in item_ids])

        return char_id

    # -------------------------------------------------------------------- GET
    @classmethod
    def get(cls, character_id: int) -> Character:
        with get_db_connection() as db:
            row = db.execute(f"SELECT * FROM {cls.TABLE} WHERE id = ?",
                             (character_id,)).fetchone()
            if row is None:
                raise KeyError(f"Character {character_id} not found")

            # reconstruct JSON cols then add junction data
            obj_data = cls._decode(row)                   # decodes abilities/skills

            obj_data["class_id"] = [r["class_id"] for r in
                db.execute("SELECT class_id FROM character_classes WHERE character_id=?", (character_id,))]
            obj_data["subclass_id"] = [r["subclass_id"] for r in
                db.execute("SELECT subclass_id FROM character_subclasses WHERE character_id=?", (character_id,))]
            obj_data["features"] = [r["feature_id"] for r in
                db.execute("SELECT feature_id FROM character_features WHERE character_id=?", (character_id,))]
            items_rows = db.execute(
                "SELECT item_id, equipped FROM character_items WHERE character_id=?",
                (character_id,)).fetchall()
            obj_data["items"]          = [r["item_id"] for r in items_rows]
            obj_data["equipped_items"] = [r["item_id"] for r in items_rows if r["equipped"]]

            return cls.MODEL(**obj_data)

    # ---------------------------------------------------------------- LIST ALL
    @classmethod
    def list_all(cls) -> List[Character]:
        with get_db_connection() as db:
            ids = [r["id"] for r in db.execute("SELECT id FROM characters")]
        return [cls.get(i) for i in ids]

    # ------------------------------------------------------------------ UPDATE
    @classmethod
    def update(cls, character_id: int, **updates: Any) -> None:
        """
        Overwrite scalar / JSON cols and completely refresh any lists
        that appear in `updates`.
        """
        # Extract possible list fields first
        list_fields = {
            "class_id":        updates.pop("class_id",      None),
            "subclass_id":     updates.pop("subclass_id",   None),
            "features":        updates.pop("features",      None),
            "items":           updates.pop("items",         None),
            "equipped_items":  updates.pop("equipped_items", None),
        }

        # ---------- 1) update scalar & JSON columns
        if updates:
            encoded = cls._encode(updates)
            sets, vals = zip(*encoded.items())
            with get_db_connection() as db:
                db.execute(f"UPDATE {cls.TABLE} SET "
                           f"{', '.join(f'{c}=?' for c in sets)} WHERE id = ?",
                           (*vals, character_id))

        # ---------- 2) resync junction tables IF the caller supplied that list
        with get_db_connection() as db:
            if list_fields["class_id"] is not None:
                db.execute("DELETE FROM character_classes WHERE character_id=?", (character_id,))
                db.executemany(
                    "INSERT INTO character_classes (character_id, class_id, level_in_class) VALUES (?, ?, ?)",
                    [(character_id, cid, 1) for cid in list_fields["class_id"]])
            if list_fields["subclass_id"] is not None:
                db.execute("DELETE FROM character_subclasses WHERE character_id=?", (character_id,))
                db.executemany(
                    "INSERT INTO character_subclasses (character_id, subclass_id) VALUES (?, ?)",
                    [(character_id, sid) for sid in list_fields["subclass_id"]])
            if list_fields["features"] is not None:
                db.execute("DELETE FROM character_features WHERE character_id=?", (character_id,))
                db.executemany(
                    "INSERT INTO character_features (character_id, feature_id) VALUES (?, ?)",
                    [(character_id, fid) for fid in list_fields["features"]])
            if list_fields["items"] is not None or list_fields["equipped_items"] is not None:
                # If only equipped list is provided, infer items list from it, or vice-versa
                items          = list_fields["items"] or []
                equipped_items = set(list_fields["equipped_items"] or [])
                if not items:
                    items = list(equipped_items)          # equipped ⊆ items guarantee
                db.execute("DELETE FROM character_items WHERE character_id=?", (character_id,))
                db.executemany(
                    "INSERT INTO character_items (character_id, item_id, equipped) VALUES (?, ?, ?)",
                    [(character_id, iid, 1 if iid in equipped_items else 0) for iid in items])
