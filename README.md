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

## Using the Game Object Wizard

`GameObjectWizard` drives a simple step based flow.  Each call to
``apply`` requires the current revision number which the wizard returns in the
previous response.  The example below creates a basic weapon item and finalises
it without saving:

```python
from pathlib import Path
from better5e.dao import FileDAO
from better5e.wizard import GameObjectWizard

wiz = GameObjectWizard(FileDAO(Path("data")))
sid = wiz.start("item")

# step 0 -> core
resp = wiz.apply(sid, {"name": "Longsword"}, revision=0)

# step 1 -> type specific
resp = wiz.apply(
    sid,
    {"category": "weapon", "damage": "1d8", "damage_type": "slashing"},
    revision=1,
)

# modifiers & grants skipped
resp = wiz.apply(sid, {"modifiers": []}, revision=2)
resp = wiz.apply(sid, {"grants": []}, revision=3)

print(wiz.preview(sid))
obj = wiz.finalize(sid, save=False)
print(obj["uuid"])
```

The wizard only mutates its internal session state; all returned structures are
plain JSON serialisable data.
