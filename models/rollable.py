from pydantic import BaseModel

class Rollable(BaseModel):
    """ A Class representing a Rollable object. """
    roll_str: str

    def __str__(self) -> str:
        """ Returns a string representation of the Rollable object. """
        return self.roll_str
    
    def roll(self) -> int:
        num, sides = map(int, self.roll_str.split('d'))
        from random import randint
        """ Simulates rolling the dice represented by the Rollable object. """
        return sum(randint(1, sides) for _ in range(num))