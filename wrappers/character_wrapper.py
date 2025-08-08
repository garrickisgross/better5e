from store.game_obj import GameObject
from wrappers.live_object import LiveObject
from schema.factory import hydrate
from uuid import UUID

class LiveCharacter(LiveObject):

    def __init__(self, game_obj: GameObject):
        super().__init__(game_obj)
        self.features: list = []
        self.load_features()
    
    def grant(self, id: UUID) -> None:
        pass

    def load_features(self) -> None:
        for feature_id in getattr(self.data, "features", []):
            feature_obj = hydrate(self.dao.get_by_id(feature_id))
            self.features.append(feature_obj)
            for mod in feature_obj.modifiers:
                if mod.op in {"set", "add"}:
                    self.set_data(mod.target, mod.value, mod.op)
                elif mod.op == "grant":
                    self.grant(mod.value)
                else:
                    raise ValueError("Modifier operation is invalid")
                

    
