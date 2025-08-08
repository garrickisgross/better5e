from store.dao import GameObjectDAO
from store.game_obj import GameObject
from schema.factory import hydrate
from typing import Any

class LiveObject:
    
    def __init__(self, game_object: GameObject):
        self.dao = GameObjectDAO()
        self.raw = game_object
        self.data = hydrate(game_object)

    def _navigate(self, target: Any, keys: list[str]) -> Any:
        """Traverse nested dictionaries/objects and return the final target."""
        for k in keys:
            if isinstance(target, dict):
                if k not in target:
                    raise AttributeError(f"Key '{k}' not found in {type(target)}")
                target = target[k]
            else:
                if not hasattr(target, k):
                    raise AttributeError(f"Attribute: '{k}' not found in {type(target)}")
                target = getattr(target, k)
        return target

    def set_data(self, path: str, value: Any, op: str) -> None:
        keys = path.split(".")
        parent = self._navigate(self.raw.data, keys[:-1])
        final_key = keys[-1]

        if isinstance(parent, dict):
            if final_key not in parent:
                raise AttributeError(f"Key '{final_key}' not in {type(parent)}")
            if op == "set":
                parent[final_key] = value
            elif op == "add":
                parent[final_key] += value
            else:
                raise ValueError("Unsupported operation")
        else:
            if not hasattr(parent, final_key):
                raise AttributeError(f"Attribute: '{final_key}' not found in {type(parent)}")
            if op == "set":
                setattr(parent, final_key, value)
            elif op == "add":
                setattr(parent, final_key, getattr(parent, final_key) + value)
            else:
                raise ValueError("Unsupported operation")

        self.process_change()
    
    def process_change(self) -> None:
        self.data = hydrate(self.raw)
        self.dao.update(self.raw)
