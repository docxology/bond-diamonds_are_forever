# Diamonds Are Forever — CONFLICT STONE · DIAMOND NET

Special-agent mission software for the BOND film package **Diamonds Are Forever
(1971)** — mission codename **CONFLICT STONE** (deepening phase: **DIAMOND NET**).

This package fuses seven deterministic, real-data analyses into a single
auditable special-agent report:

| Concept | Module | Covers |
|---|---|---|
| Smuggled-goods provenance | `provenance_chain.py` | Conflict-diamond custody graph, documented handoffs, break points |
| Corridor routing | `smuggling_routes.py` | Risk-weighted corridor network, Dijkstra least-risk route, survival, reduction |
| Lot forensics | `lot_forensics.py` | Weight-gain / excess-loss / density-mismatch audit, verdict |
| Casino money movement | `casino_network.py` | Inter-casino transfers, hub, money cycles, laundering closure |
| Benford ledger audit | `benford_audit.py` | Leading-digit law test, chi-square statistic, anomalous verdict |
| Orbital targeting | `orbital_mirror.py` | Line-of-sight, slant range, elevation geometry |
| Beam delivery | `beam_physics.py` | Diffraction spot, atmospheric attenuation, concentration, vaporization, minimum mirror |

The analytic cores are **pure** (stdlib math, no infrastructure imports), and
`src/diamonds_are_forever/mission.py` is a thin adapter implementing the frozen
`bond-api` `MissionProvider` protocol (brief → recon → plan → execute →
debrief), consumed as a local path dependency.

## Headline results (all computed at runtime)

- Provenance: 5 handoffs, 2 break points, 60% documented coverage.
- Routing: 10 corridors; optimum route cuts seizure cost 16% vs the naive one.
- Forensics: lot DF-71 is **flagrant** (2 weight/density anomalies).
- Casino: 7 casinos, 77% laundering closure, hub = `whyte_house`.
- Benford: the 101-transaction ledger is **anomalous** (chi-square 44.06).
- Orbital: 2 of 3 targets visible at 36,000 km.
- Beam: a 43 m mirror is the honest minimum to deliver 1 MW/m² at GEO.

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
src/diamonds_are_forever/   pure core (7 modules) + mission adapter + figures + manifest vars
scripts/                    thin phase CLIs and generators
tests/                      deterministic tests (coverage-gated, zero mocks)
manuscript/                 config + numbered sections (`{{TOKEN}}`-driven)
docs/                       agent instructions, architecture, testing philosophy
```
