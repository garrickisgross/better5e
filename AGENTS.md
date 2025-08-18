# AGENTS

## Overview
- Outline the purpose and scope of this repository.
- Highlight key goals and ongoing initiatives.

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
