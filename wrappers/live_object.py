from store.dao import GameObjectDAO
from store.game_obj import GameObject
from schema.factory import hydrate
from schema.primitives import Modifier
from typing import Any
from uuid import UUID

class LiveObject:
    
    def __init__(self, game_object: GameObject):
        self.dao = GameObjectDAO()
        self.raw = game_object
        self.data = hydrate(game_object)

    def set_data(self, path: str, value: Any, op: str) -> None:
        keys = path.split(".")
        target = self.raw.data
        final_key = keys[-1]
        for k in keys[:-1]:

            if isinstance(target, dict):
                if k not in target:
                    raise AttributeError(f"Key '{k}' not found to edit")
                target = target[k]

            else:
                if not hasattr(target, k):
                    raise AttributeError(f"Attribute: '{k}' not found in {type(target)}")
                target = getattr(target, k)
                
        if isinstance(target, dict):
            
            if final_key not in target:
                raise AttributeError(f"Key '{final_key}' not in {type(target)}")
            
            if op == "set":
                target[final_key] = value
            elif op == "add":
                target[final_key] += value
        else:
            if not hasattr(target, final_key):
                raise AttributeError(f"Attribute: '{final_key}' not found in {type(target)}")
            if op == "set":
                setattr(target, final_key, value)
            elif op == "add":
                setattr(target, final_key, getattr(target, final_key) + value)
            else:
                raise ValueError("Unsupported operation")

        self.process_change()
    
    def process_change(self) -> None:
        self.data = hydrate(self.raw)
        self.dao.update(self.raw)






        
                

    
