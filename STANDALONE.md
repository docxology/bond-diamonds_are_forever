# Standalone Package Guide — CONFLICT STONE

`diamonds_are_forever` is a **standalone BOND film package** whose analytic
core is pure and infrastructure-free. It depends only on the frozen `bond-api`
protocol (a local path dependency) plus standard scientific libraries.

## Purpose

Special-agent mission software for *Diamonds Are Forever* (1971): a
deterministic, auditable analysis of (1) a smuggled conflict-diamond provenance
chain, (2) Las Vegas casino money movement, and (3) orbital-mirror targeting
geometry — exposed through the BOND-API `MissionProvider` lifecycle.

## Local-only

This is a **local-only working tree**: there is no remote, and nothing in this
package may be pushed. Metadata sidecars (`.zenodo.json`, `CITATION.cff`,
`codemeta.json`) therefore carry **no DOI or repository fields**.

## What this package guarantees

- Pure domain core with **no** `infrastructure.*` or `bond_api` imports —
  importable standalone.
- Deterministic: frozen canonical datasets, fixed seed, no RNG, no wall-clock
  in persisted artifacts.
- Zero mocks: all tests run real computations over real data.
- Covered: `uv run pytest tests/ --cov=src --cov-fail-under=90` (≥90% gate).
- Protocol-frozen: the mission adapter implements the frozen `bond-api`
  `MissionProvider` contract; the orchestrator discovers it by slug
  `diamonds_are_forever`.

## Run it

```bash
uv sync --extra dev
uv run python scripts/run_mission.py --json
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Validation from this directory

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```
