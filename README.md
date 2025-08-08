# Better5e

Better5e is a small Python library for modeling concepts from Dungeons & Dragons® 5th Edition. It provides Pydantic-powered data models for characters, races, features, items and other game objects, making it easier to build tooling around the 5e ruleset.

## Installation

Clone the repository and install the dependencies:

```bash
git clone <repo>
cd better5e
pip install -r requirements.txt
```

## Example

The `examples.py` script demonstrates constructing a character, persisting data and rolling dice:

```python
from pathlib import Path
from better5e.character import Character
from better5e.dao import FileDAO
from better5e.game_objects import Feature, Race
from better5e.modifiers import Modifier, ModifierOperation
from better5e.rollable import Roll

stealth_mod = Modifier(target="stats.dexterity", operation=ModifierOperation.ADD, value=2)
darkvision = Feature(name="Darkvision")
elf = Race(name="Elf", modifiers=[stealth_mod], grants=[darkvision.uuid])

dao = FileDAO(Path("data"))
dao.save(darkvision)
dao.save(elf)

char = Character(name="Arannis", race=elf)
char.apply_grants(dao)
print("Dexterity:", char.get_stat("dexterity"))
print("Features:", [f.name for f in char.features])

roll = Roll("1d20+3")
print("Roll:", roll.evaluate())
```

This example matches the one in `examples.py` and can be run directly:

```bash
python examples.py
```
