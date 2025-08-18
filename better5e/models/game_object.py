from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import Annotated, Union, Literal, Optional
from better5e.models.enums import *


class Modifier(BaseModel):
    target: str # Character attribute (dot notation for nested)
    op: Op
    value: int | None = None # If "getting" we set the value at runtime as it can change

class Rollable(BaseModel):
    num: int = 1
    sides: int = 20
    modifier: Modifier | None = None

class Action(BaseModel):
    action_type: ActionType
    roll: Rollable | None = None

class Base(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: UUID = Field(default_factory=uuid4)
    kind: str
    name: str
    desc: str | None = None
    actions: list[Action] = Field(default_factory=list)
    modifiers: list[Modifier] = Field(default_factory=list)
    grants: list[UUID] = Field(default_factory=list)

class Feature(Base):
    kind: Literal["feature"] = "feature"
    desc: str
    uses_max: int | None = None
    recharge: RechargeType | None = None

class Spellcasting(Base):
    kind: Literal["spellcasting"] = "spellcasting"
    caster_type: Literal["prepared", "known"]
    slots_per_level: dict[int, int] # Num spell slots per level.
    spells_known_per_level: dict[int, int] # num spell slots known
    spell_list: list[UUID]

class Spell(Base):
    kind: Literal["spell"] = "spell"
    components: list[str] | None = None

class ItemBase(Base):
    value: int
    weight: int

class Weapon(ItemBase):
    kind: Literal["weapon"] = "weapon"
    properties: list[str] = Field(default_factory=list)

class Consumable(ItemBase):
    kind: Literal["consumable"] = "consumable"
    roll: Rollable | None = None

class Armor(ItemBase):
    kind: Literal["armor"] = "armor"
    base_ac: int
    max_dex_bonus: int


AnyGameObj = Annotated[Union[Spell, Feature, Weapon, Spellcasting, Consumable, Armor], Field(discriminator='kind')]