from enum import Enum

from models.modifier import Modifier


class FeatureType(str, Enum):
    CLASS = "class feature"
    RACIAL = "racial feature"
    FEAT = "feat"
    SPELL = "spell"
    ITEM = "item"
    ABILITY = "ability"
    OTHER = "other"  # For any other types not covered above

class ActionType(str, Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus action"
    REACTION = "reaction"
    FREE_ACTION = "free action"
    NONE = "none"  # For features that don't require an action
    SPECIAL = "special"  # For unique cases that don't fit standard action types

class FeaturePrerequisiteType(str, Enum):
    LEVEL = "level"
    CLASS = "class"
    SUBCLASS = "subclass"
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    PROFICIENCY = "proficiency"
    SKILL = "skill"
    FEAT = "feat"
    OTHER = "other"  # For any other types not covered above


class RechargeType(str, Enum):
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    DAWN = "dawn"