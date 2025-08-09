# Better 5e

Better 5e provides a small set of Pydantic models and a SQLite-backed data access layer for building tooling around the 5th Edition of the world's greatest roleplaying game.

## Game Objects

`better5e.models.game_object` defines the core data structures used across the project.  All objects inherit from a common `Base` type and are discriminated by a `kind` field so they can be stored and retrieved generically.  Available object types include features, weapons, spellcasting profiles, consumables and armor, each with fields tailored to their behaviour.

## Data Access

`better5e.dao.sqlite.DAO` is a singleton that persists any game object to an on-disk SQLite database.  On initialisation it applies the schema from `startup.sql` and exposes `save`, `load_by_id`, and `load_by_kind` helpers for working with stored objects.

## Quickstart

```bash
python main.py  # populates the database with sample features
```

## Running Tests

Install dependencies and execute the test suite with coverage:

```bash
python -m pip install -r requirements.txt
pytest --cov=better5e --cov-report=term-missing
```

The project includes a small example test ensuring that the DAO round-trips data correctly while achieving full code coverage.
