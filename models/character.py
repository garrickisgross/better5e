from typing import Any
from uuid import UUID
from engine.rules_engine import RulesEngine
from engine.state import CharacterState


class Character:

    def __init__(self, state: CharacterState, rules: RulesEngine):
        self.state = state
        self.rules = rules

    @property
    def totals(self) -> dict[str, Any] :
        return self.rules.compute(self.state)
    
    def long_rest(self):
        self.rules.apply_event(self.state, "long_rest")
        self.state._mod_cache.clear()
    
    def add_asset(self, asset_id: UUID):
        self.state.asset_ids.append(asset_id)
        self.state._mod_cache.clear()
    