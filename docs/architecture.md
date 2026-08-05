# Architecture — diamonds_are_forever (CONFLICT STONE)

## OverView

```
src/diamonds_are_forever/
  provenance_chain.py      pure core — custody graph, break points, coverage, origin
  smuggling_routes.py      pure core — expected-cost corridor routing, survival, reduction
  lot_forensics.py         pure core — weight/density reconciliation audit + verdict
  casino_network.py        pure core — directed weighted transfers, hub, cycles, closure
  benford_audit.py         pure core — leading-digit Benford law + chi-square verdict
  orbital_mirror.py        pure core — occultation, slant range, elevation geometry
  beam_physics.py          pure core — diffraction spot, attenuation, vaporization, min mirror
  mission.py               adapter — MissionProvider (brief/recon/plan/execute/debrief)
  manuscript_variables.py  {{TOKEN}} hydration (config.yaml + pure core)
  figures.py               deterministic figure generation (7 PNGs)
scripts/
  brief.py recon.py plan.py execute.py debrief.py   phase CLIs
  run_mission.py           full flow (+ --json)
  generate_figures.py      renders output/figures/*.png
  z_generate_manuscript_variables.py  hydrates output/manuscript/*
tests/                     deterministic tests, zero mocks
manuscript/                config.yaml + numbered sections ({{TOKEN}}s)
```

## Layer contract

| Layer | Depends on | Import rules |
|---|---|---|
| Pure core (`provenance_chain`, `smuggling_routes`, `lot_forensics`, `casino_network`, `benford_audit`, `orbital_mirror`, `beam_physics`) | stdlib only (`beam_physics` re-uses `orbital_mirror` constants) | NO `bond_api`, NO `infrastructure` |
| Adapter (`mission`) | pure core + `bond_api` | sole importer of `bond_api` |
| Manifest/figures | pure core + `yaml`/`matplotlib` | reads `manuscript/config.yaml` |
| Scripts | adapter / core | thin orchestration only |

The pure core is deliberately infrastructure-free so it stays importable even
if the `bond-api` path dependency is ever unavailable (a stated fallback).

## Data flow

1. Frozen canonical datasets live as `canonical_*()` factories in each pure
   module (single source of truth).
2. The adapter (`mission.py`) calls them during `execute()` to compute the
   outcome's `results` and a SHA-256 `input_hash`.
3. `manuscript_variables.py` calls the same factories to compute `{{TOKEN}}`
   values — so the manuscript and the mission outcome can never disagree.
4. `figures.py` renders the same data to `output/figures/`.

## Determinism

- No RNG anywhere; the mission seed is a constant (7).
- `Provenance.wall_time_s` is always 0; input fingerprints are SHA-256 over the
  sorted JSON of canonical inputs.
- Network adjacency iteration follows insertion order; casino lists are sorted
  alphabetically.
