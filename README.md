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

## Game Object Wizard

The `GameObjectWizard` offers a step-based builder for creating game objects
with type-aware forms. The snippet below shows building a simple weapon item:

```python
from pathlib import Path
from better5e.dao import FileDAO
from better5e.wizard import GameObjectWizard

wiz = GameObjectWizard(FileDAO(Path("data")))
sid = wiz.start("item")

# core step
wiz.apply(sid, {"name": "Longsword", "type": "item"})

# type-specific fields
wiz.apply(sid, {
    "data": {
        "category": "weapon",
        "damage": "1d8",
        "damage_type": "slashing",
        "properties": ["versatile"],
    }
})

# modifiers and grants steps (empty in this example)
wiz.apply(sid, {"modifiers": []})
wiz.apply(sid, {"grants": []})

preview = wiz.preview(sid)
result = wiz.finalize(sid, save=False)
print(preview)
print(result["model"]["name"])
```

Running this snippet prints a preview summary and the finalized object's name.
