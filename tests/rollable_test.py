from models.rollable import Rollable

def test_rollable_str():
    """ Test the string representation of a Rollable object. """
    rollable = Rollable(roll_str="2d6")
    assert str(rollable) == "2d6"

def test_rollable_roll():
    """ Test the roll method of a Rollable object. """
    rollable = Rollable(roll_str="2d6")
    result = rollable.roll()
    assert isinstance(result, int)
    assert 2 <= result <= 12
