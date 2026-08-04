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

1. **Pure core** (`src/diamonds_are_forever/provenance_chain.py`,
   `casino_network.py`, `orbital_mirror.py`): stdlib math only; **no**
   `bond_api` / `infrastructure` imports; importable standalone.
2. **Adapter** (`src/diamonds_are_forever/mission.py`): the only module that
   imports `bond_api`; implements the frozen `MissionProvider` contract.
3. **Manifest/figures** (`manuscript_variables.py`, `figures.py`): read the
   pure core + `manuscript/config.yaml`.
4. **Scripts** (`scripts/`): thin orchestrators; bootstrap `src/` and forward
   to the core/adapter.

## Before changing code

- Consult `docs/architecture.md` before altering module boundaries.
- Consult `docs/testing_philosophy.md` before writing/modifying `pytest` files.
- Update `manuscript/` sections + `manuscript_variables.py` together whenever
  a behaviour change alters a metric; never hand-author a number in prose.
- Regenerate `output/` artifacts (`generate_figures.py`,
  `z_generate_manuscript_variables.py`) so the tree stays consistent.
