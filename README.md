# Better5e

Better5e is an experimental toolkit for representing Dungeons & Dragons 5th Edition data in Python.  
It uses [Pydantic](https://docs.pydantic.dev/) models to describe game objects, a small SQLite-backed store for persistence and "live" wrappers that operate on the stored data.

## Project structure

- `schema/` &ndash; Pydantic models for 5e data including characters, classes, races, spells and a factory (`schema.factory.hydrate`) for turning stored data into typed models.
- `store/` &ndash; SQLite persistence layer built around a generic `GameObject` model and a `GameObjectDAO` with CRUD helpers.
- `wrappers/` &ndash; Runtime helpers. `LiveObject` allows in-place updates to nested data while keeping the backing store in sync, and `LiveCharacter` loads features, backgrounds and spellcasting for a hydrated character.
- `tests/` &ndash; Pytest based unit tests for the models, DAO and wrappers.

## Getting started

The repository is not yet packaged for distribution. To experiment with it locally, clone the repo and install the requirements:

```bash
git clone <repo>
cd better5e
pip install -r requirements.txt
```

You can then create and hydrate objects:

```python
from store.game_obj import GameObject
from schema.factory import hydrate

raw = GameObject(name="Fighter", type="class", data={}, tags=[])
model = hydrate(raw)
print(model)

# set up the SQLite DB (creates better5e_v1.db)
import sqlite3, pathlib
db_path = pathlib.Path("better5e_v1.db")
if not db_path.exists():
    conn = sqlite3.connect(db_path)
    conn.executescript(open("store/startup.sql").read())
    conn.close()
```

## CLI frontend

A minimal command line interface is available for creating Better5e objects. After installing the requirements, launch it with:

```bash
python -m cli.main
```

Follow the prompts to create features, classes, subclasses, spellcasting, spells, items, and characters. When a field
requires an existing object, use the built-in search to look up objects by name and select the desired entry instead of
typing raw UUIDs.

## Running tests

Tests live in the `tests/` directory and can be executed with:

```bash
pytest
```

## Status

This project is under active development and many features are incomplete or subject to change.

