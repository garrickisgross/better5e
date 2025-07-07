from typing import Annotated, Any, Literal, Optional
from pydantic import BaseModel, Field, StringConstraints
from uuid import UUID, uuid4
from datetime import datetime

StatKeyType = Annotated[str, StringConstraints(min_length=3, max_length=3, pattern="^[A-Z_]+$")]
SkillKeyType = Annotated[str, StringConstraints(min_length=5, max_length=5, pattern="^[A-Z_]+$")]

class Stat(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    key: StatKeyType
    name: str
    description: str = ""
    default: bool = False

class Skill(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    key: SkillKeyType
    name: str
    governing_stat_key: StatKeyType
    default: bool

    @staticmethod
    def validate_gov_stat(skill, all_stats:dict[str, Stat]):
        if skill.governing_stat_key not in all_stats:
            raise ValueError(f"Stat {skill.governing_stat_key} does not exist")

class Modifier(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target_key: str
    op: Literal["add", "set"]
    value: int

    def validate_key(self, all_stats: dict[str, Stat], all_skills:dict[str, Skill]):
        if self.target_key not in all_stats and self.target_key not in all_skills:
            raise ValueError(f"Unknown Target: {self.target_key}")

class Asset(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["stat", "skill", "spell", "item"
                  "feature", "class", "subclass", "resource"]
    
    name: str
    text: str = ""
    tags: list[str] = []
    data: Optional[dict[str, Any]] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class FeatureData(BaseModel):
    action_cost: str | None = None
    modifiers: list[Modifier] = []
    grants: list[UUID] = []

class SpellData(BaseModel):
    pass

class ItemData(BaseModel):
    pass

class ClassData(BaseModel):
    pass    

class SubClassData(BaseModel):
    pass 

class ResourceData(BaseModel):
    pass 

