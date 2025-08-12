## Developer Notes

### Testing
- Always run `pytest --cov=better5e` and ensure 100% coverage before committing.

### Imports
- Use absolute import paths; do **not** convert existing imports to relative ones.

### Main screen layout
- The home screen uses a `QSplitter` (`self.split`) whose sizes are persisted in `QSettings` under `ui/home_splitter`.

