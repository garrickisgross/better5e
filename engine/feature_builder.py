from models.enums import FeaturePrerequisiteType, FeatureType, ActionType, RechargeType
from models.feature import Feature
from transitions import Machine
from typing import Any, Self

from models.modifier import Modifier
from models.rollable import Rollable

class FeatureBuilder:
    def __init__(self):
        self._data: dict[str, Any] = {}

    def name(self, name:str) -> Self:

        self._data["name"] = name
        return self
    
    def description(self, desc: str) -> Self:

        self._data["description"] = desc
        return self
    
    def prerequisite(self, kind: FeaturePrerequisiteType, value: Any) -> Self:
        
        if "prerequisites" in self._data.keys():
            self._data["prerequisites"] += {kind: value}
        else:
            self._data["prerequisites"] = [{kind: value}]
        return self
    
    def prerequisites_text(self, text: str) -> Self:

        self._data["prerequisites_text"] = text
        return self
    
    def feature_type(self, ftype: FeatureType) -> Self:

        self._data["feature_type"] = ftype
        return self
    
    def action_type(self, atype: ActionType):

        self._data["action_type"] = atype
        return self
    
    def uses(self, count: int) -> Self:

        self._data["uses"] = count
        return self
    
    def recharge(self, text: RechargeType) -> Self:

        self._data["recharge"] = text
        return self
    
    def grant_feature(self, feature_id: int) -> Self:
        
        if "granted_features" in self._data.keys():
            self._data["granted_features"] += feature_id
        else:
            self._data["granted_features"] = [feature_id]

        return self
    
    def grant_spell(self, spell_id: int) -> Self:
        
        if "granted_spells" in self._data.keys():
            self._data["granted_spells"] += spell_id
        else:
            self._data["granted_spells"] = [spell_id]

        return self
    
    def grant_item(self, item_id: int) -> Self:

        if "granted_items" in self._data.keys():
            self._data["granted_items"] += item_id
        else:
            self._data["granted_items"] = [item_id]

        return self
    
    def grant_modifier(self, mod: Modifier) -> Self:

        if "modifiers" in self._data.keys():
            self._data["modifiers"] += mod
        else:
            self._data["modifiers"] = [mod]

        return self
    
    def add_rollable(self, rollable: Rollable) -> Self:

        self._data["rollable"] = rollable
        return self

    def add_feature_option(self, opt: int) -> Self:

        if "options" in self._data.keys():
            self._data["options"] += opt
        else:
            self._data["options"] = [opt]

        return self
    
    def choice_count(self, num: int) -> Self:

        self._data["choice_count"] = num
        return self
    
    def build(self) -> Feature:
        
        return Feature(**self._data)
    
