# diamonds_are_forever — CONFLICT STONE TODO

Forward-only backlog for the BOND film package **Diamonds Are Forever (1971)**.

## What is built (phase 2)

| Module | Concept |
|---|---|
| `src/diamonds_are_forever/provenance_chain.py` | Conflict-diamond custody graph; break points; coverage; origin tracing |
| `src/diamonds_are_forever/casino_network.py` | Directed weighted casino transfers; net/gross flow; hub; money cycles; laundering closure |
| `src/diamonds_are_forever/orbital_mirror.py` | Orbital-mirror targeting: occultation, slant range, elevation, beam delivery |
| `src/diamonds_are_forever/mission.py` | `MissionProvider` adapter (CONFLICT STONE) + gadget registration + input fingerprint |
| `src/diamonds_are_forever/manuscript_variables.py` | `{{TOKEN}}` hydration from `manuscript/config.yaml` + analytic core |
| `src/diamonds_are_forever/figures.py` | Deterministic provenance / casino / orbital figures |

Thin CLIs in `scripts/`: `brief.py`, `recon.py`, `plan.py`, `execute.py`,
`debrief.py`, `run_mission.py`, `generate_figures.py`,
`z_generate_manuscript_variables.py`.

## Verification evidence

- `uv run pytest tests/ --cov=src --cov-fail-under=90` → passing, ~98% coverage
  (floor 90%).
- ruff `check` + `format` clean on `src/` and `scripts/`; mypy clean on
  `src/` and `scripts/`.
- Lineage `rg template[_]code_project` → zero in tracked source.
- Deterministic: end-to-end `run_mission.py` is byte-stable; mission outcomes
  carry a SHA-256 input fingerprint.

## Declared integration points

- **bond-api protocol (FROZEN)**: implemented. `mission.py` adapts the frozen
  `MissionProvider` contract from the local `bond-api` path dependency.
- **bond-utilities provenance**: not yet consumed. Integration point: delegate
  outcome persistence to `bond_utilities.mission_io.record_provenance_outcome`
  once bond-utilities ships. Acceptance: a mission record lands under
  `output/data/` with a full `provenance` block. Until then the package keeps
  its own `mission_input_hash` (SHA-256) — no rework needed to bind.
- **orchestrator discovery**: `mission.py` exposes `MissionProvider` at module
  top level under the stable name; the orchestrator will discover it by slug
  `diamonds_are_forever` via `bond_api.discovery`.

## Improvement ladder

1. Add a provenance-export CLI that writes canonical inputs + outcome to JSON
   (feeds the bond-utilities integration point).
2. Surface more orbital targets / a per-target elevation table in the figure.
3. Add optional sensitivity sweeps over mirror area / spot radius behind the
   deterministic defaults.
4. Refresh `docs/_generated/COUNTS.md` equivalents only if this tree is ever
   wired back into the monorepo pipeline (currently standalone/local-only).
