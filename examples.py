"""Basic example usage of the Better5e models."""

from pathlib import Path

from better5e.character import Character
from better5e.dao import FileDAO
from better5e.game_objects import Feature, Race
from better5e.modifiers import Modifier, ModifierOperation
from better5e.rollable import Roll


def main() -> None:
    # Create a race that grants a feature and a dexterity bonus
    stealth_mod = Modifier(target="stats.dexterity", operation=ModifierOperation.ADD, value=2)
    darkvision = Feature(name="Darkvision")
    elf = Race(name="Elf", modifiers=[stealth_mod], grants=[darkvision.uuid])

    dao = FileDAO(Path("data"))
    dao.save(darkvision)
    dao.save(elf)

    # Build a character and hydrate grants
    char = Character(name="Arannis", race=elf)
    char.apply_grants(dao)
    print(f"Dexterity: {char.get_stat('dexterity')}")
    print("Features:", [f.name for f in char.features])

    # Roll an ability check
    roll = Roll("1d20+3")
    print("Roll:", roll.evaluate())


if __name__ == "__main__":
    main()
