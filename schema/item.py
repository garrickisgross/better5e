from pydantic import BaseModel, Field
from typing import Literal

from schema.primitives import Modifier
from schema.rollable import Rollable


class Item(BaseModel):
    category: Literal["weapon", "consumable", "armor"]
    equipped: bool = False
    modifiers: list[Modifier]
    attack_modifier: int | None = None
    damage_dice: str | None = None
    damage_modifier: int | None = None
    rollables: dict[str, Rollable] = Field(default_factory=dict)

    def __init__(self, **data):
        rollables = data.get("rollables", {})
        if rollables:
            data["rollables"] = {k: Rollable.model_validate(v) for k, v in rollables.items()}
        super().__init__(**data)
