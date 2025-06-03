from pydantic import BaseModel

class Resource(BaseModel):
    """ Represents a resource in the system. """
    name: str
    description: str = None
    charges: int

    
    