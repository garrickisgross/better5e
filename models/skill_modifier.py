from pydantic import BaseModel

class SkillModifier(BaseModel):
    """ Represents a skill modifier in the system. """
    skill: str
    modifier: int