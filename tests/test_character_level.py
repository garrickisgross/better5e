from uuid import uuid4
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from schema.character import Character, CharacterClass
from schema.primitives import AbilityScore, Skill


def test_character_level_sum():
    first = CharacterClass(class_id=uuid4(), level=3)
    second = CharacterClass(class_id=uuid4(), level=2)

    ability_scores = {
        "str": AbilityScore(proficient=False, value=10, modifier=0)
    }
    skills = {
        "acrobatics": Skill(proficient="none", modifier=0)
    }

    character = Character(
        ac=10,
        ability_scores=ability_scores,
        proficiency_bonus=2,
        skills=skills,
        background=uuid4(),
        features=[],
        inventory=[],
        classes=[first, second],
        spellcasting=None,
    )

    assert character.level == 5
