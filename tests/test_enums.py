from better5e.enums import AbilityScore, Skill, ProficiencyLevel, DamageType


def test_enums_exist():
    assert AbilityScore.STR.value == "strength"
    assert Skill.ACROBATICS.value == "acrobatics"
    assert ProficiencyLevel.PROFICIENT.value == "proficient"
    assert DamageType.FIRE.value == "fire"
