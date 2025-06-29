class Rollable:
    """Mixin class for objects that can be rolled (e.g., dice rolls)."""

    def roll(self):
        """Roll the object (e.g., a die) and return the result."""
        raise NotImplementedError("Roll method must be implemented by subclasses.")