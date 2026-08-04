# Style — src/

Python conventions for `diamonds_are_forever`.

- **Formatter**: `ruff format` (line length 100 per `pyproject.toml`).
- **Linter**: `ruff check` — run after every edit.
- **Types**: `mypy` clean on `src/`; full annotations on public APIs.
- **No mocks**: tests use real data + computation only.
- **Ordering**: imports grouped stdlib → third-party → local.
- **Naming**: `snake_case` functions/variables; `UPPER_CASE` constants;
  dataclasses for value objects.
- **Documentation**: module docstrings explain the concept; function docstrings
  cover args/returns/raises where non-trivial.
