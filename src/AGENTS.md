# src/ — AGENTS.md

Rules for the source tree of `diamonds_are_forever`.

## Layer contract (enforced)

- `provenance_chain.py`, `casino_network.py`, `orbital_mirror.py` are **pure**:
  stdlib math only. No `bond_api`, no `infrastructure`, no I/O. They must stay
  importable standalone.
- `mission.py` is the **only** module importing `bond_api`; it adapts the core
  to the frozen `MissionProvider` contract and registers gadgets.
- `manuscript_variables.py` / `figures.py` read the core + config; they may
  import `yaml` / `matplotlib` but not `bond_api`.

## Conventions

- Type hints + docstrings on all public functions/classes.
- Deterministic: canonical datasets via `canonical_*()` factories; no RNG.
- Run `uv run ruff check src/` + `uv run ruff format` + `uv run mypy src/`
  before committing. See `STYLE.md` for format details.
