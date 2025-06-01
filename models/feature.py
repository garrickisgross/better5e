from models.item import Item
from models.spell import Spell
from models.weapon import WeaponType
from typing import Tuple, Optional , Any, Self

class Feature:
    """A class representing a feature in the application."""

    weapon_attack_modifier: Optional[int] = None
    weapon_attack_type: Optional[WeaponType] = None
    weapon_damage_type: Optional[Any] = None        # TODO: Define DamageType when we are creating damage types
    weapon_damage_dice: Optional[Any]               # TODO: Define Dice type when we are creating dice roller
    weapon_damage_modifier: Optional[int] = None
    spell_attack_modifier: Optional[int] = None
    spell_damage_modifier: Optional[int] = None
    spell_save_dc_modifier: Optional[int] = None
    skill_modifier: Optional[Tuple[str, int]]
    save_modifier: Optional[Tuple[str, int]]  # Tuple of (save_type, modifier)
    stat_modifier: Optional[Tuple[str, int]]  # Tuple of (stat_type, modifier)
    item: Optional[Item] = None
    spell: Optional[Spell] = None
    feature: Optional[Self] = None


    
    def __init__(self, name: str, description: str, **kwargs):
        """Initialize a feature with a name, description, and optional properties."""
        self.name = name
        self.description = description

        self.properties = [
            "weapon_attack_modifier",
            "weapon_attack_type",
            "weapon_damage_type",
            "weapon_damage_dice",
            "weapon_damage_modifier",
            "spell_attack_modifier",
            "spell_damage_modifier",
            "spell_save_dc_modifier",
            "skill_modifier",
            "save_modifier",
            "stat_modifier",
            "item",
            "spell",
            "feature",
        ]
        for prop in self.properties:
            if prop in kwargs:
                setattr(self, prop, kwargs[prop])

