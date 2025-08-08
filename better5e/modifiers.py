from __future__ import annotations

"""Modifier system for Better5e."""

from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ModifierOperation(str, Enum):
    ADD = "add"
    MULTIPLY = "multiply"
    SET = "set"
    GRANT = "grant"


class Modifier(BaseModel):
    """Represents a modification to a target attribute."""

    id: UUID = Field(default_factory=uuid4)
    target: str
    operation: ModifierOperation
    value: Any
    condition: Optional[str] = None
    stackable: bool = True

    def apply(self, base_value: Any) -> Any:
        """Apply this modifier to *base_value* and return the result.

        Grant operations simply return ``base_value``; it's up to the consumer to
        interpret grants separately.
        """

        if self.operation == ModifierOperation.ADD:
            return base_value + self.value
        if self.operation == ModifierOperation.MULTIPLY:
            return base_value * self.value
        if self.operation == ModifierOperation.SET:
            return self.value
        # GRANT does not change the base value directly
        return base_value
