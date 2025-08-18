# AGENTS

## Scope
These guidelines apply to all files under `better5e/UI`.

## UI Guidelines
- Keep widgets focused and well documented.
- Use type hints throughout.
- Prefer composition over inheritance when designing UI components.
- Emit Qt signals for interaction rather than directly invoking callbacks.
- List-based widgets should expose their underlying item order via an ``items``
  attribute so tests can verify state without a running event loop.
