from store.game_obj import GameObject
from wrappers.live_object import LiveObject
from schema.factory import hydrate
from uuid import UUID
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
        self.apply_background()
        self.load_features()
        self.load_spellcasting()
        self.load_items()
    
    def grant(self, id: UUID) -> None:
        pass

    def apply_background(self) -> None:
        background_id = getattr(getattr(self, "data", None), "background", None)
        if not background_id:
            return
        background_obj = hydrate(self.dao.get_by_id(background_id))
        for mod in background_obj.modifiers:
            if mod.op in {"set", "add"}:
                self.set_data(mod.target, mod.value, mod.op)
            elif mod.op == "grant":
                self.grant(mod.value)
            else:
                raise ValueError("Modifier operation is invalid")
        
    def _load_race(self) -> None:
        data = getattr(self, "data", None)
        race_id = getattr(data, "race", None)
        if not race_id:
            return
        race_obj = hydrate(self.dao.get_by_id(race_id))
        for feature_id in race_obj.features:
            feature_obj = hydrate(self.dao.get_by_id(feature_id))
            self.features.append(feature_obj)
        for mod in race_obj.modifiers:
            if mod.op in {"set", "add"}:
                self.set_data(mod.target, mod.value, mod.op)
            elif mod.op == "grant":
                self.grant(mod.value)
            else:
                raise ValueError("Modifier operation is invalid")

    def load_features(self) -> None:
        if not getattr(self, "features", None):
            data = getattr(self, "data", None)
            self.features = []
            for feature_id in getattr(data, "features", []):
                feature_obj = hydrate(self.dao.get_by_id(feature_id))
                self.features.append(feature_obj)
            self._load_race()
        for feature_obj in self.features:
            for mod in feature_obj.modifiers:
                if mod.op in {"set", "add"}:
                    self.set_data(mod.target, mod.value, mod.op)
                elif mod.op == "grant":
                    self.grant(mod.value)
                else:
                    raise ValueError("Modifier operation is invalid")

    def load_spellcasting(self) -> None:
        spellcasting_map = {}
        spells_map = {}
        for class_entry in getattr(getattr(self, "data", {}), "classes", []):
            class_obj = self.dao.get_by_id(class_entry.class_id)
            hydrated_class = hydrate(class_obj)
            spellcasting_id = getattr(hydrated_class, "spellcasting", None)
            if spellcasting_id:
                sc_obj = self.dao.get_by_id(spellcasting_id)
                hydrated_sc = hydrate(sc_obj)
                spellcasting_map[class_obj.name] = hydrated_sc.model_dump()
                spells_map[class_obj.name] = [
                    hydrate(self.dao.get_by_id(spell_id))
                    for spell_id in hydrated_sc.spell_list
                ]
        if spellcasting_map:
            self.raw.data.setdefault("spellcasting", {}).update(spellcasting_map)
            self.process_change()
        self.spells = spells_map

    def load_items(self) -> None:
        data = getattr(self, "data", None)
        self.items = []
        for item_id in getattr(data, "inventory", []):
            item_obj = hydrate(self.dao.get_by_id(item_id))
            self.items.append(item_obj)
            if getattr(item_obj, "equipped", False):
                for mod in item_obj.modifiers:
                    if mod.op in {"set", "add"}:
                        self.set_data(mod.target, mod.value, mod.op)
                    elif mod.op == "grant":
                        self.grant(mod.value)
                    else:
                        raise ValueError("Modifier operation is invalid")
                

    
