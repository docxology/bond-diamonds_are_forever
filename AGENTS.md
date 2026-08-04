# diamonds_are_forever — AGENTS.md

BOND film package **Diamonds Are Forever (1971)** · mission codename **CONFLICT
STONE**. One package in the PROJECT BOND suite at
`projects/working/bond/` (local-only working tree, no remote).

## Scope & guardrails

- **Scope is exactly this directory.** Never touch sibling bond packages, bond
  root files, or the template repo.
- **Local-only.** No remote; never push.
- **Path-scoped commits**: `git add -A` inside this repo only.
- **No mock framework.** Real data + computation only.
- **≥90% line+branch coverage** on `src/`: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
- **Deterministic**: fixed canonical datasets, fixed seed, no untracked RNG, no
  wall-clock in persisted artifacts.
- **Thin orchestrators** in `scripts/`; business logic in `src/`.

## Layer contract

| Surface | Rule |
|---|---|
| `src/diamonds_are_forever/provenance_chain.py`, `casino_network.py`, `orbital_mirror.py` | Pure domain core — stdlib math only, **no** `bond_api`/`infrastructure` imports; importable standalone |
| `src/diamonds_are_forever/mission.py` | Thin adapter — implements the frozen `bond_api.protocol.MissionProvider`; registers gadgets |
| `src/diamonds_are_forever/manuscript_variables.py`, `figures.py` | Manifest/figures over the pure core |
| `scripts/` | Thin CLIs (brief/recon/plan/execute/debrief, run_mission, figure + manuscript-variable generators) |

## Protocol integration

- Depends on `bond-api` via `[tool.uv.sources]` path dependency; run
  `uv sync --extra dev` before pytest.
- `src/diamonds_are_forever/mission.py` exposes `MissionProvider` at module top
  level (stable name) so the orchestrator discovers it by slug
  `diamonds_are_forever`.
- Pure core stays importable without `bond-api` (fallback if the path dep ever
  fails).

## Reference files

- `docs/agent_instructions.md` — operational constraints.
- `docs/architecture.md` — module boundaries before altering `src/`/`scripts/`.
- `docs/testing_philosophy.md` — before writing/modifying `pytest` files.
- `manuscript/SYNTAX.md` — manuscript token + figure protocol.
