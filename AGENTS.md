# AGENTS

## Overview
- Better5e provides a small set of **Pydantic** models, a **SQLite**-backed data access layer, and a **PyQt6** 
  frontend for homebrewing characters and campaigns for the 5th Edition of the world’s greatest role-playing game.

- A **data-driven** 5e toolkit: users define custom **Features**, **Items**, **Spells**, **Classes/Subclasses**, **Modifiers**, and **Rollables** that flow through a rules engine.
- A **desktop UI** in PyQt6 for browsing, creating, and editing homebrew content.
- A **simple DAO** over SQLite for persistence.

**Key goals:** correctness of rules interactions, predictable persistence, crisp UI patterns, and maintainable code.

## Production expectations

Better5e is intended to be a **production-grade desktop application**. Code should be written with maintainability, testability, and stability in mind. UI components must feel polished and consistent with professional-grade software. Avoid quick hacks—prefer patterns that scale, with attention to accessibility, responsiveness, and cross-platform behavior.

## Architecture
- Core application code lives under `better5e/` with tests in `better5e/tests/`.
- `main.py` acts as the entry point for launching the app.
- Maintain clear separation of concerns between UI, data access, and business logic.

## Code Guidelines
- Follow PEP 8 and format code with `black` and `isort`.
- Keep imports tidy and run `ruff` for linting.
- Prefer type hints and validate with `mypy` or `pyright`.
- Document public interfaces and keep functions small and focused.

## PR Template
- **Summary**: Brief description of the change and motivation.
- **Testing**: Evidence of test runs or screenshots.
- **Screenshots**: Required for UI changes.
- **Checklist**: Confirm lint, tests, and documentation updates.

## UI/UX Guidelines (Modern UI/UX/Production Grade)
- Strive for a clean, responsive, and accessible interface.
- Use consistent theming and spacing to match a modern look.
- Optimize for keyboard and screen reader accessibility.
- Keep interactions intuitive and provide meaningful feedback.

## Testing Requirements (Aim for 100% Coverage)
- Write tests for new features and edge cases.
- Run `pytest --cov` to monitor coverage.
- Avoid merging if coverage decreases or critical paths lack tests.

## Environment Setup
- Use Python 3.11+ and create a virtual environment.
- Install dependencies via `pip install -r requirements.txt`.
- Activate the virtual environment for development and testing.
- Run the application with `python main.py`.
