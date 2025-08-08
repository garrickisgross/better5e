import random
import re
from typing import ClassVar
from pydantic import BaseModel, model_validator


class Rollable(BaseModel):
    dice: str
    modifier: int | str = 0

    _notation_re: ClassVar[re.Pattern] = re.compile(r"^(?:(\d*)d(\d+))(?:([+-]\d+))?\Z", re.IGNORECASE)
    _dice_re: ClassVar[re.Pattern] = re.compile(r"^(?:(\d*)d(\d+))\Z", re.IGNORECASE)

    def __init__(self, *args, **data):
        if args:
            if len(args) != 1 or data:
                raise TypeError("Rollable accepts a single positional argument or keyword arguments")
            data = self._coerce(args[0])
        else:
            data = self._coerce(data) if isinstance(data, (int, str)) else data
        super().__init__(**data)

    @classmethod
    def model_validate(cls, v, **kwargs):
        data = cls._coerce(v)
        return super().model_validate(data, **kwargs)

    @classmethod
    def _validate_before(cls, v):
        return cls._coerce(v)

    # Expose validator to pydantic while keeping _validate_before callable
    _pydantic_validate_before = model_validator(mode="before")(_validate_before.__func__)

    @classmethod
    def _coerce(cls, v):
        if isinstance(v, cls):
            return v.model_dump()
        if isinstance(v, dict):
            return v
        if isinstance(v, int):
            return {"dice": "1d20", "modifier": v}
        if isinstance(v, str):
            n = v.strip()
            if n.isdigit() or (n.startswith("-") and n[1:].isdigit()):
                return {"dice": "1d20", "modifier": int(n)}
            m = cls._notation_re.fullmatch(n)
            if not m:
                raise ValueError(f"Invalid dice notation: {n}")
            count = m.group(1)
            sides = m.group(2)
            mod = int(m.group(3)) if m.group(3) else 0
            dice = f"{count}d{sides}" if count else f"d{sides}"
            return {"dice": dice, "modifier": mod}
        raise TypeError("Rollable must be int, str, or dict")

    def roll(self, character=None) -> int:
        m = self._dice_re.fullmatch(self.dice)
        if not m:
            raise ValueError(f"Invalid dice notation: {self.dice}")
        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
        total = sum(random.randint(1, sides) for _ in range(count))
        total += self._resolve_modifier(character)
        return total

    def _resolve_modifier(self, character) -> int:
        if isinstance(self.modifier, int):
            return self.modifier
        if isinstance(self.modifier, str):
            if character is None:
                raise ValueError("Character is required to resolve modifier")
            abilities = getattr(character, "ability_scores", {})
            if self.modifier in abilities:
                return abilities[self.modifier].modifier
            skills = getattr(character, "skills", {})
            if self.modifier in skills:
                return skills[self.modifier].modifier
            attr = getattr(character, self.modifier, None)
            if isinstance(attr, int):
                return attr
            raise ValueError(f"Unknown modifier reference: {self.modifier}")
        raise TypeError("Modifier must be int or str")

