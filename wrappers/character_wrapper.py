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
        self.load_features()
        self.load_spellcasting()
    
    def grant(self, id: UUID) -> None:
        pass

    def load_features(self) -> None:
        if not getattr(self, "features", None):
            feature_ids = getattr(getattr(self, "data", {}), "features", [])
            self.features = []
            for feature_id in feature_ids:
                feature_obj = hydrate(self.dao.get_by_id(feature_id))
                self.features.append(feature_obj)
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
                spellcasting_map[class_obj.name] = hydrated_sc.dict()
                spells_map[class_obj.name] = [
                    hydrate(self.dao.get_by_id(spell_id))
                    for spell_id in hydrated_sc.spell_list
                ]
        if spellcasting_map:
            self.raw.data.setdefault("spellcasting", {}).update(spellcasting_map)
            self.process_change()
        self.spells = spells_map
                

    
