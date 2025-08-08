from __future__ import annotations

"""Rollable interface for Better5e."""

from dataclasses import dataclass
import random
import re
from typing import Iterable, List

from .modifiers import Modifier


def _parse_expression(expr: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", expr.replace(" ", ""))
    if not match:
        raise ValueError(f"Invalid dice expression: {expr}")
    count = int(match.group(1)) if match.group(1) else 1
    die = int(match.group(2))
    mod = int(match.group(3)) if match.group(3) else 0
    return count, die, mod


@dataclass
class Roll:
    """Simple dice roll expression."""

    expression: str
    advantage: bool = False
    disadvantage: bool = False

    def _roll_once(self) -> int:
        count, die, mod = _parse_expression(self.expression)
        total = sum(random.randint(1, die) for _ in range(count)) + mod
        return total

    def evaluate(self, modifiers: Iterable[Modifier] | None = None) -> int:
        rolls: List[int] = [self._roll_once()]
        if self.advantage or self.disadvantage:
            rolls.append(self._roll_once())
        result = max(rolls) if self.advantage else min(rolls) if self.disadvantage else rolls[0]
        for m in modifiers or []:
            if m.target == "roll":
                result = m.apply(result)
        return result
