# diamonds_are_forever — CONFLICT STONE · DIAMOND NET TODO

Forward-only backlog for the BOND film package **Diamonds Are Forever (1971)**.

## What is built

### Phase 2 — CONFLICT STONE (three concepts)

| Module | Concept |
|---|---|
| `src/diamonds_are_forever/provenance_chain.py` | Conflict-diamond custody graph; break points; coverage; origin tracing |
| `src/diamonds_are_forever/casino_network.py` | Directed weighted casino transfers; net/gross flow; hub; money cycles; laundering closure |
| `src/diamonds_are_forever/orbital_mirror.py` | Orbital-mirror targeting: occultation, slant range, elevation, beam power |
| `src/diamonds_are_forever/mission.py` | `MissionProvider` adapter (CONFLICT STONE) + gadget registration + input fingerprint |

### Phase 4 — DIAMOND NET (deepening)

| Module | Concept | Algorithm |
|---|---|---|
| `smuggling_routes.py` | Which corridor the goods travel | Expected-cost Dijkstra over seizure-risk corridors + fewest-hops BFS baseline → reduction |
| `lot_forensics.py` | Physical laundering of the lot | Weight-gain / excess-loss / density-mismatch audit with a clean/suspicious/flagrant verdict |
| `benford_audit.py` | Laundering signature of the ledger | Leading-digit Benford law + Pearson chi-square at df=8 / alpha=0.05 |
| `beam_physics.py` | What the orbital weapon delivers | Diffraction spot, Beer-Lambert attenuation, power budget, vaporization, minimum mirror diameter |

The mission adapter, `manuscript_variables.py`, and `figures.py` were deepened
to consume the four new modules (7 figures, ~37 `{{TOKEN}}`s).

## Verification evidence

- `uv run pytest tests/ --cov=src --cov-fail-under=90` → passing, ~98% coverage
  (floor 90%), 189 tests, 0 failures / 0 skipped / no mocks.
- ruff `check` + `format` clean on `src/` and `scripts/`; mypy clean on
  `src/` and `scripts/` (20 files).
- Lineage `rg template[_]code_project` → zero literal hits in tracked source.
- Deterministic: end-to-end `run_mission.py` is byte-stable; mission outcomes
  carry a SHA-256 input fingerprint including the new canonical inputs.

## Declared integration points

- **bond-api protocol (FROZEN)**: implemented. `mission.py` adapts the frozen
  `MissionProvider` contract; public shape unchanged across deepening.
- **bond-utilities provenance**: not yet consumed. Integration point: delegate
  outcome persistence to `bond_utilities.mission_io.record_provenance_outcome`
  once bond-utilities ships. Until then the package keeps its own
  `mission_input_hash` (SHA-256) — no rework needed to bind.
- **orchestrator discovery**: `mission.py` exposes `MissionProvider` at module
  top level under the stable name; the orchestrator discovers it by slug
  `diamonds_are_forever` via `bond_api.discovery`.

## Improvement ladder

1. Add a provenance-export CLI that writes canonical inputs + outcome to JSON
   (feeds the bond-utilities integration point).
2. Add a dynamic satellite scheduling pass over the new beam physics (strike
   energy budget across the visible target set).
3. Widen the forensic module with a paste-vs-diamond spectroscopy channel.
4. Refresh `docs/_generated/COUNTS.md` equivalents only if this tree is ever
   wired back into the monorepo pipeline (currently standalone/local-only).
