# Better5e

Better5e is an experimental toolkit for representing Dungeons & Dragons 5th Edition data in Python. The project is built around [Pydantic](https://docs.pydantic.dev/) models and includes a simple SQLite-backed data store and helper wrappers for working with "live" game objects.

## Project structure

- `schema/` &ndash; Core data models such as `Character`, `Class`, `Subclass`, and `Feature`.
- `store/` &ndash; Persistence layer that defines a `GameObject` model and DAO helpers for SQLite storage.
- `wrappers/` &ndash; Higher level helpers that operate on stored objects at runtime.

## Getting started

The repository is not yet packaged for distribution. To experiment with it locally, clone the repo and install the requirements:

```bash
git clone <repo>
cd better5e
pip install pydantic
```

You can then create and hydrate objects:

```python
from store.game_obj import GameObject
from schema.factory import hydrate

raw = GameObject(name="Fighter", type="class", data={}, tags=[])
model = hydrate(raw)
print(model)
```

## Status

This project is under active development and many features are incomplete or subject to change.

