# src/ — diamonds_are_forever (CONFLICT STONE)

Pure analytic core + mission adapter for the BOND film package.

| Module | Role | Imports |
|---|---|---|
| `provenance_chain.py` | conflict-diamond custody graph, break points, coverage, origin | stdlib only |
| `casino_network.py` | Las Vegas money movement: hub, cycles, laundering closure | stdlib only |
| `orbital_mirror.py` | orbital targeting: occultation, slant range, beam delivery | stdlib only |
| `mission.py` | `MissionProvider` adapter (CONFLICT STONE) + gadgets | core + `bond_api` |
| `manuscript_variables.py` | `{{TOKEN}}` hydration | core + `yaml` |
| `figures.py` | deterministic PNG figures | core + `matplotlib` |

The first three modules are **pure** and importable without `bond_api`;
`mission.py` is the thin, sole adapter to the frozen protocol.
