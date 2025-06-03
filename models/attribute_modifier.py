from pydantic import BaseModel

class AttributeModifier(BaseModel):
    """ Represents an attribute modifier in the system. """
    attribute: str
    modifier: int