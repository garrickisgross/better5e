import random
import re
from pydantic import RootModel, field_validator


class Rollable(RootModel[str]):
    @field_validator('root', mode='before')
    @classmethod
    def _coerce_notation(cls, v):
        if isinstance(v, int):
            return str(v)
        if isinstance(v, str):
            return v.strip()
        raise TypeError('Rollable must be int or dice notation string')

    _dice_re = re.compile(r"^(?:(\d*)d(\d+))(?:([+-]\d+))?\Z", re.IGNORECASE)

    def roll(self) -> int:
        n = self.root
        if n.isdigit() or (n.startswith('-') and n[1:].isdigit()):
            return random.randint(1, 20) + int(n)
        m = self._dice_re.fullmatch(n)
        if not m:
            raise ValueError(f'Invalid dice notation: {n}')
        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
        mod = int(m.group(3)) if m.group(3) else 0
        total = sum(random.randint(1, sides) for _ in range(count)) + mod
        return total
