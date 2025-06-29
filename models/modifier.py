from enum import Enum
from pydantic import BaseModel


class OperationType(str, Enum):
    """Enum for operation types."""
    ADD = "add"
    MULTIPLY = "multiply"
    OVERRIDE = "override"

class ModifierTarget(str, Enum):
    """Enum for modifier targets."""
    HEALTH = "health"
    DAMAGE = "damage"
    ATTACK = "attack"
    SAVE = "save"
    ATTRIBUTE = "attribute"
    SKILL = "skill"

class Modifier(BaseModel):
    target: ModifierTarget
    operation: OperationType
    target_name: str
    value: int

    def apply(self, base_value: int) -> int:
        """Applies the modifier to a base value."""
        if self.operation == OperationType.ADD:
            return base_value + self.value
        elif self.operation == OperationType.MULTIPLY:
            return base_value * self.value
        elif self.operation == OperationType.OVERRIDE:
            return self.value
        else:
            raise ValueError(f"Unknown operation type: {self.operation}")