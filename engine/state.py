from dataclasses import dataclass
from uuid import UUID
from pydantic import Field


@dataclass
class ResourceState:
    max: int
    current: int
    recharge: str | None = None

@dataclass
class CharacterState:
    ability_scores: dict[str, int]
    skill_proficiencies: set[str]
    asset_ids: list[UUID]
    level_map: dict[str, int]
    resources: dict[UUID, ResourceState] = Field(default_factory=dict)
    conditions: set[str] = Field(default_factory=set)
    _mod_cache: list[UUID] = Field(default_factory=list, init=False)

