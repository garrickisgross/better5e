from store.game_obj import GameObject
from wrappers.live_object import LiveObject
from schema.factory import hydrate
from schema.rollable import Rollable
from uuid import UUID
from collections import deque
import builtins

class LiveCharacter(LiveObject):

    def __init__(self, game_obj: GameObject):
        # Use the built-in ``super`` to avoid accidental shadowing of the
        # function via monkeypatching, ensuring the LiveObject initializer is
        # always invoked.
        builtins.super(LiveCharacter, self).__init__(game_obj)
        self.features: list = []
        self.spells: dict = {}
        self.items: list = []
        self.rollables: dict[str, dict[str, Rollable]] = getattr(self.data, "rollables", {})
        self.apply_background()
        self.load_features()
        self.load_spellcasting()
        self.load_items()

    def _mount_rollables(self, name: str, rollables: dict[str, Rollable] | None) -> None:
        if not rollables:
            return
        raw_rollables = self.raw.data.setdefault("rollables", {})
        for action, roll in rollables.items():
            raw_rollables.setdefault(action, {})[name] = roll.model_dump()
            self.rollables.setdefault(action, {})[name] = roll
        self.process_change()
        self.rollables = self.data.rollables

    def _apply_modifier(self, mod, queue: deque | None = None, seen: set[UUID] | None = None) -> None:
        """Apply a single modifier to the character."""
        if mod.op in {"set", "add"}:
            self.set_data(mod.target, mod.value, mod.op)
        elif mod.op == "grant":
            if queue is not None and seen is not None:
                if mod.value not in seen:
                    queue.append(mod.value)
            else:
                grant_fn = getattr(self, "grant", None)
                if grant_fn is None:
                    LiveCharacter.grant(self, mod.value)
                else:
                    grant_fn(mod.value)
        else:
            raise ValueError("Modifier operation is invalid")

    def _apply_modifiers(self, modifiers, queue: deque | None = None, seen: set[UUID] | None = None) -> None:
        """Apply a list of modifiers using :py:meth:`_apply_modifier`."""
        for mod in modifiers:
            LiveCharacter._apply_modifier(self, mod, queue, seen)

    def grant(self, id: UUID) -> None:
        # ``grant`` may be invoked in unit tests with incomplete dummy
        # objects.  If the instance lacks a DAO, there is nothing we can do.
        if not hasattr(self, "dao"):
            return

        # Utilize a FIFO queue to ensure breadth-first application of
        # grants.  ``deque`` gives us ``popleft`` for efficient FIFO
        # semantics.
        queue: deque[UUID] = deque([id])
        seen: set[UUID] = set()

        while queue:
            current_id = queue.popleft()
            if current_id in seen:
                continue
            seen.add(current_id)

            game_obj = self.dao.get_by_id(current_id)
            hydrated = hydrate(game_obj)

            obj_type = getattr(game_obj, "type", None)

            if obj_type == "feature":
                # Track the feature on the character and persist it to the
                # raw data if not already present.
                self.features.append(hydrated)
                feats = self.raw.data.setdefault("features", [])
                if current_id not in feats:
                    feats.append(current_id)
                    self.process_change()
                modifiers = hydrated.modifiers
            elif obj_type == "item":
                # Add the item to the inventory and persist if new.
                self.items.append(hydrated)
                inv = self.raw.data.setdefault("inventory", [])
                if current_id not in inv:
                    inv.append(current_id)
                    self.process_change()
                # Only apply modifiers from equipped items, mirroring the
                # behaviour of ``load_items``.
                modifiers = hydrated.modifiers if getattr(hydrated, "equipped", False) else []
            else:
                # Unknown types may still have modifiers, so we attempt to
                # process them generically.
                modifiers = getattr(hydrated, "modifiers", [])

            name = getattr(game_obj, "name", str(current_id))
            LiveCharacter._mount_rollables(self, name, getattr(hydrated, "rollables", {}))

            for mod in modifiers:
                if mod.op == "grant" and mod.value not in seen:
                    queue.append(mod.value)
                else:
                    LiveCharacter._apply_modifier(self, mod, queue, seen)

    def apply_background(self) -> None:
        background_id = getattr(getattr(self, "data", None), "background", None)
        if not background_id:
            return
        bg_obj = self.dao.get_by_id(background_id)
        background_obj = hydrate(bg_obj)
        LiveCharacter._mount_rollables(self, getattr(bg_obj, "name", str(background_id)), getattr(background_obj, "rollables", {}))
        LiveCharacter._apply_modifiers(self, background_obj.modifiers)
        
    def _load_race(self) -> None:
        data = getattr(self, "data", None)
        race_id = getattr(data, "race", None)
        if not race_id:
            return
        race_go = self.dao.get_by_id(race_id)
        race_obj = hydrate(race_go)
        LiveCharacter._mount_rollables(self, getattr(race_go, "name", str(race_id)), getattr(race_obj, "rollables", {}))
        for feature_id in race_obj.features:
            feature_go = self.dao.get_by_id(feature_id)
            feature_obj = hydrate(feature_go)
            self.features.append(feature_obj)
            LiveCharacter._mount_rollables(self, getattr(feature_go, "name", str(feature_id)), getattr(feature_obj, "rollables", {}))
        LiveCharacter._apply_modifiers(self, race_obj.modifiers)

    def load_features(self) -> None:
        if not getattr(self, "features", None):
            data = getattr(self, "data", None)
            self.features = []
            for feature_id in getattr(data, "features", []):
                feature_go = self.dao.get_by_id(feature_id)
                feature_obj = hydrate(feature_go)
                self.features.append(feature_obj)
                LiveCharacter._mount_rollables(self, getattr(feature_go, "name", str(feature_id)), getattr(feature_obj, "rollables", {}))
            self._load_race()
        for feature_obj in self.features:
            LiveCharacter._apply_modifiers(self, feature_obj.modifiers)

    def load_spellcasting(self) -> None:
        spellcasting_map = {}
        spells_map = {}
        for class_entry in getattr(getattr(self, "data", {}), "classes", []):
            class_obj = self.dao.get_by_id(class_entry.class_id)
            hydrated_class = hydrate(class_obj)
            LiveCharacter._mount_rollables(self, getattr(class_obj, "name", str(class_entry.class_id)), getattr(hydrated_class, "rollables", {}))
            spellcasting_id = getattr(hydrated_class, "spellcasting", None)
            if spellcasting_id:
                sc_obj = self.dao.get_by_id(spellcasting_id)
                hydrated_sc = hydrate(sc_obj)
                LiveCharacter._mount_rollables(self, getattr(sc_obj, "name", str(spellcasting_id)), getattr(hydrated_sc, "rollables", {}))
                spellcasting_map[class_obj.name] = hydrated_sc.model_dump()
                spells_map[class_obj.name] = []
                for spell_id in hydrated_sc.spell_list:
                    spell_obj = self.dao.get_by_id(spell_id)
                    spell = hydrate(spell_obj)
                    spells_map[class_obj.name].append(spell)
                    LiveCharacter._mount_rollables(self, getattr(spell_obj, "name", str(spell_id)), getattr(spell, "rollables", {}))
        if spellcasting_map:
            self.raw.data.setdefault("spellcasting", {}).update(spellcasting_map)
            self.process_change()
        self.spells = spells_map

    def load_items(self) -> None:
        data = getattr(self, "data", None)
        self.items = []
        for item_id in getattr(data, "inventory", []):
            item_go = self.dao.get_by_id(item_id)
            item_obj = hydrate(item_go)
            self.items.append(item_obj)
            LiveCharacter._mount_rollables(self, getattr(item_go, "name", str(item_id)), getattr(item_obj, "rollables", {}))
            if getattr(item_obj, "equipped", False):
                LiveCharacter._apply_modifiers(self, item_obj.modifiers)
                

    
