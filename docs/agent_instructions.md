# Agent Instructions — diamonds_are_forever (CONFLICT STONE)

Operational constraints for any agent (human or AI) working inside this BOND
film package.

## Scope

Work **only** inside `projects/working/bond/diamonds_are_forever/`. Do not
touch sibling bond packages, the bond root, or the template repo. This is a
**local-only** tree — there is no remote and nothing is pushed.

## Guardrails

- **No mocks.** No `MagicMock` / `mocker.patch` / `unittest.mock`. Real data +
  computation only.
- **Determinism.** Fixed canonical datasets, fixed seed, no untracked RNG, no
  wall-clock in persisted artifacts. Re-running produces byte-identical output.
- **Coverage.** `uv run pytest tests/ --cov=src --cov-fail-under=90`.
- **Tooling.** `uv run ruff check src/ scripts/` + `uv run ruff format` +
  `uv run mypy src/ scripts/` all clean.
- **Lineage.** No `template[_]code_project` strings in tracked source.

## Layer boundaries

1. **Pure core** — all seven analysis modules:
   `provenance_chain.py`, `smuggling_routes.py`, `lot_forensics.py`,
   `casino_network.py`, `benford_audit.py`, `orbital_mirror.py`,
   `beam_physics.py`. Stdlib math only; **no** `bond_api` / `infrastructure`
   imports; importable standalone. `beam_physics` may read the
   `SOLAR_CONSTANT_W_M2` constant from `orbital_mirror` — that is the only
   permitted cross-module reference, and it must stay a constant, not
   behaviour.
2. **Adapter** (`src/diamonds_are_forever/mission.py`): the only module that
   imports `bond_api`; implements the frozen `MissionProvider` contract.
3. **Manifest/figures** (`manuscript_variables.py`, `figures.py`): read the
   pure core + `manuscript/config.yaml`.
4. **Scripts** (`scripts/`): thin orchestrators; bootstrap `src/` and forward
   to the core/adapter. No business logic — if you are tempted to compute
   something in `scripts/`, it belongs in `src/`.

## The frozen surface — do not change these shapes

`bond-cli`, the coordinator's reconcile pass, and the orchestrator consume
these across packages. Deepen inside them; never alter their public shape.

- `MissionProvider.film` and the five lifecycle methods
  `brief` / `recon` / `plan` / `execute` / `debrief`, including their return
  dataclasses.
- `register_gadgets(registry)` and the eleven registered gadget **names**.
- The module-level name `MissionProvider` in `mission.py` (discovery resolves
  the slug `diamonds_are_forever` to it).

## Before changing code

- Consult `docs/architecture.md` before altering module boundaries, and read
  its *Numerical cautions* section before touching `first_digit` or
  `trace_origin` — both have non-obvious correct implementations.
- Consult `docs/testing_philosophy.md` before writing/modifying `pytest` files.
- Update `manuscript/` sections + `manuscript_variables.py` together whenever
  a behaviour change alters a metric; never hand-author a number in prose. A
  new quantitative claim means a new variable **and** a new token — and the
  expected-key set in `tests/test_manuscript_variables.py` must be updated, or
  the suite will tell you.
- Model constants the manuscript cites (thresholds, critical values,
  requirements) belong in the owning module as named, exported constants and
  reach the prose as tokens.
- Regenerate `output/` artifacts (`generate_figures.py`,
  `z_generate_manuscript_variables.py`) so the tree stays consistent.
- Do not add a guard that cannot fail. If an invariant is structural, assert it
  in a test; a dead branch reads as safety while verifying nothing.
