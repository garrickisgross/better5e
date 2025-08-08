from store.game_obj import GameObject
from wrappers.live_object import LiveObject
from uuid import UUID

class LiveCharacter(LiveObject):

    def __init__(self, game_obj: GameObject):
        super.__init__(game_obj)
        self.load_features()
    
    def grant(self, id: UUID) -> None:
        pass

    def load_features(self) -> None:
        for f in self.features:
            for mod in f.modifiers:
                if mod.op == "set" or mod.op == "add":
                    self.set_data(mod.target, mod.value, mod.op)
                elif mod.op == "grant":
                    self.grant(mod.value)
                else:
                    raise ValueError("Modifier operation is invalid")
                

    
