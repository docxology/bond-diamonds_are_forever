# tests/ — diamonds_are_forever (CONFLICT STONE · DIAMOND NET)

Deterministic, coverage-gated, mock-free test suite.

| File | Covers |
|---|---|
| `test_provenance_chain.py` | custody graph, break points, coverage, origin, validation |
| `test_smuggling_routes.py` | expected-cost routing (Dijkstra + BFS), survival, reduction, validation |
| `test_lot_forensics.py` | weight/density audit rules, verdicts, validation |
| `test_casino_network.py` | transfers, hub, cycles, laundering closure, validation |
| `test_benford_audit.py` | leading-digit law, chi-square, report verdict, negative control, validation |
| `test_orbital_mirror.py` | occultation, slant range, elevation, beam power, validation |
| `test_beam_physics.py` | diffraction, attenuation, vaporization, min-mirror, validation |
| `test_mission.py` | MissionProvider lifecycle, protocol, discovery, gadgets, serialization |
| `test_manuscript_variables.py` | token map + live `{{TOKEN}}` cross-reference gate |
| `test_figures.py` | 7 deterministic PNG figures |
| `test_scripts_smoke.py` | subprocess phase-CLI + generator smoke |

Run: `uv run pytest tests/ --cov=src --cov-fail-under=90`. See
`../docs/testing_philosophy.md` for the conventions.
