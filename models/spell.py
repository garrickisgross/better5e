from pydantic import BaseModel
import uuid

class Spell(BaseModel):
    """ Represents a spell in the system. """
    id: uuid.UUID = uuid.uuid4()  # Default to a new UUID
    name: str
    description: str = ""
    level: int = 0
    school: str = ""
    casting_time: str = "1 action"
    range: str = "30 feet"
    components: str = "V, S"
    duration: str = "Instantaneous"

    # Is Save spell
    is_save_spell: bool = False

