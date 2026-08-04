# Diamonds Are Forever — CONFLICT STONE

Special-agent mission software for the BOND film package **Diamonds Are Forever
(1971)** — mission codename **CONFLICT STONE**.

This package fuses three deterministic, real-data analyses into a single
auditable special-agent report:

| Concept | Module | Covers |
|---|---|---|
| Smuggled-goods provenance | `src/diamonds_are_forever/provenance_chain.py` | Conflict-diamond custody graph, documented handoffs, provenance break points |
| Casino money movement | `src/diamonds_are_forever/casino_network.py` | Las Vegas inter-casino transfers, net positions, laundering closure, hub casino |
| Orbital-mirror targeting | `src/diamonds_are_forever/orbital_mirror.py` | Space-mirror line-of-sight, slant range, elevation, beam delivery geometry |

The analytic cores are **pure** (stdlib math, no infrastructure imports), and
`src/diamonds_are_forever/mission.py` is a thin adapter implementing the frozen
`bond-api` `MissionProvider` protocol (brief → recon → plan → execute →
debrief), consumed as a local path dependency.

## Key result tokens

- Provenance: 5 handoffs, 2 break points, 60% documented coverage.
- Casino: 7 casinos, 9 transfers, $31M total flow, hub = `whyte_house`,
  3 money cycles, 77% laundering closure.
- Orbital: 3 targets at 36,000 km, 2 visible (Las Vegas, Washington DC).

All numbers are computed at runtime from frozen canonical datasets; the
manuscript reads them via `{{TOKEN}}` injection, never as hand-stated prose.

## Usage

```bash
# Install (from this directory) — wires the bond-api path dependency.
uv sync --extra dev

# Full mission flow + round-trip JSON outcome.
uv run python scripts/run_mission.py
uv run python scripts/run_mission.py --json

# Per-phase CLIs.
uv run python scripts/brief.py
uv run python scripts/recon.py
uv run python scripts/plan.py
uv run python scripts/execute.py
uv run python scripts/debrief.py

# Regenerate figures and hydrate the manuscript tree.
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

Deterministic by construction: fixed canonical datasets, no RNG, no mocks, and
every mission outcome carries a SHA-256 fingerprint of its inputs.

## Project layout

```
src/diamonds_are_forever/   pure core + mission adapter + figures + manifest vars
scripts/                    thin phase CLIs and generators
tests/                      deterministic tests (coverage-gated, zero mocks)
manuscript/                 config + numbered sections (`{{TOKEN}}`-driven)
docs/                       agent instructions, architecture, testing philosophy
```
