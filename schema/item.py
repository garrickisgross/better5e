from pydantic import BaseModel
from typing import Literal

from schema.primitives import Modifier


class Item(BaseModel):
    category: Literal["weapon", "consumable", "armor"]
    equipped: bool = False
    modifiers: list[Modifier]
    attack_modifier: int | None = None
    damage_dice: str | None = None
    damage_modifier: int | None = None
