# src/ — diamonds_are_forever (CONFLICT STONE)

Pure analytic core + mission adapter for the BOND film package.

| Module | Role | Imports |
|---|---|---|
| `provenance_chain.py` | conflict-diamond custody graph, break points, coverage, origin | stdlib only |
| `smuggling_routes.py` | risk-weighted corridor routing: expected-cost Dijkstra vs. fewest-hops BFS, survival, reduction | stdlib only |
| `lot_forensics.py` | weight-gain / excess-loss / density-mismatch audit and verdict | stdlib only |
| `casino_network.py` | Las Vegas money movement: hub, cycles, laundering closure | stdlib only |
| `benford_audit.py` | leading-digit Benford test and Pearson chi-square verdict | stdlib only |
| `orbital_mirror.py` | orbital targeting: occultation, slant range, elevation, captured power | stdlib only |
| `beam_physics.py` | diffraction spot, Beer-Lambert attenuation, power budget, minimum mirror | stdlib only (+ `SOLAR_CONSTANT_W_M2` from `orbital_mirror`) |
| `mission.py` | `MissionProvider` adapter (CONFLICT STONE) + gadgets | core + `bond_api` |
| `manuscript_variables.py` | `{{TOKEN}}` hydration | core + `yaml` |
| `figures.py` | deterministic PNG figures | core + `matplotlib` |

The first seven modules are **pure** and importable without `bond_api`;
`mission.py` is the thin, sole adapter to the frozen protocol.
