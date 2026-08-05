# src/ — AGENTS.md

Rules for the source tree of `diamonds_are_forever`.

## Layer contract (enforced)

- The pure domain modules are **pure**: stdlib math only. No `bond_api`, no
  `infrastructure`, no I/O. They must stay importable standalone:
  - `provenance_chain.py` — custody graph, break points, coverage, origin.
  - `smuggling_routes.py` — expected-cost corridor routing (Dijkstra + BFS
    baseline), survival, reduction.
  - `lot_forensics.py` — weight/density reconciliation audit + verdict.
  - `casino_network.py` — directed weighted transfers, hub, cycles, closure.
  - `benford_audit.py` — leading-digit Benford law + chi-square verdict.
  - `orbital_mirror.py` — occultation, slant range, elevation geometry.
  - `beam_physics.py` — diffraction spot, attenuation, vaporization, minimum
    mirror (imports `orbital_mirror` constants only).
- `mission.py` is the **only** module importing `bond_api`; it adapts the core
  to the frozen `MissionProvider` contract and registers gadgets. Its public
  shape (class + `register_gadgets`) is frozen across deepening.
- `manuscript_variables.py` / `figures.py` read the core + config; they may
  import `yaml` / `matplotlib` but not `bond_api`.

## Conventions

- Type hints + docstrings on all public functions/classes.
- Deterministic: canonical datasets via `canonical_*()` factories; no RNG.
- Run `uv run ruff check src/` + `uv run ruff format` + `uv run mypy src/`
  before committing. See `STYLE.md` for format details.
