
from typing import Any
from uuid import UUID
from engine.state import CharacterState
from models.primitives import Asset, Modifier
from models.types import Feature


class RulesEngine:

    def __init__(self, asset_loader):
        self.asset_loader = asset_loader

    
    
    def compute(self, char: CharacterState) -> dict[str, Any]:
        mods = self._collect_modifiers(char)
        values = self._reduce(char, mods)
        return values
    
    def apply_event(self, char: CharacterState, event: str, **kwargs):
        for asset in map(self.asset_loader, char.asset_ids):
            self._dispatch(asset, char, event, **kwargs)

    def _collect_modifiers(self, char: CharacterState) -> list[Modifier]:
        if char._mod_cache:
            return char._mod_cache
        mods = []
        for asset in map(self.asset_loader, self._expand_assets(char.asset_ids)):
            if isinstance(asset, Feature):
                mods.extend(asset.data.modifiers)
        char._mod_cache = mods

        return mods
    
    def _reduce(self, char: CharacterState, mods: list[Modifier]) -> dict[str, Any]:
        totals = char.ability_scores.copy()

        for op in ("set", "add"):
            for m in filter(lambda x: x.op == op, mods):
                key = m.target_key
                
                if op == "set":
                    totals[key] = int(m.value)
                
                if op == "add":
                    totals[key] = totals.get(key, 0) + m.value
                
        return totals
    
    def _dispatch(self, asset: Asset, char: CharacterState, event: str, **kw):
        hook = getattr(asset, f"on_{event}", None)
        if hook:
            hook(char, **kw)

    def _expand_assets(self, roots: list[UUID]) -> list[UUID]:
        seen = set(roots)
        frontier = list(roots)

        while frontier:
            new_ids: list[UUID] = []
            for aid in frontier:
                asset = self.asset_loader(aid)
                if isinstance(asset, Feature):
                    new_ids.extend(asset.data.grants)
            
            frontier = [i for i in new_ids if i not in seen]
            seen.update(frontier)

        return list(seen)
                