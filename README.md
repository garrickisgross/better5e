# Better5e

*A small, data-driven Python library for modeling Dungeons & Dragons® 5e objects with Pydantic.*

Better5e provides strongly-typed models for characters, races, features, items, rollables, and more—plus a simple persistence layer—so you can script, test, and build tooling around the 5e ruleset without wrestling with ad-hoc data structures.

> **Status:** Early work-in-progress. APIs may change.

---

## ✨ Features

- **Pydantic models** for core 5e concepts (e.g., `Character`, `Race`, `Feature`, `Item`, `Roll`).
- **Modifiers** with dot-notation targets and operations (e.g., `add`, `set`) to change stats and metadata.
- **Grants system** so features/items can grant other objects (and those can grant more…) during hydration.
- **Rollables** (`"1d20+3"`, `"2d8+2"`) you can evaluate in code and attach to actions/resources.
- **Simple persistence (FileDAO)** to save/load objects as JSON on disk; designed so other DAOs (e.g., SQLite) can slot in later.
- **Testable by design** with pure functions and typed models.

---

## 📦 Installation

```bash
git clone https://github.com/garrickisgross/better5e.git
cd better5e
python -m venv .venv && source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
