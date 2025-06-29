from pydantic import BaseModel

class Modifier(BaseModel):
    target: str
    mode: str
    value: int
