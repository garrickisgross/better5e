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
        self.apply_background()
        self.load_features()
    
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
                

    
