# tests/ — diamonds_are_forever (CONFLICT STONE)

Deterministic, coverage-gated, mock-free test suite.

| File | Covers |
|---|---|
| `test_provenance_chain.py` | custody graph, break points, coverage, origin, validation |
| `test_casino_network.py` | transfers, hub, cycles, laundering closure, validation |
| `test_orbital_mirror.py` | occultation, slant range, elevation, beam delivery, validation |
| `test_mission.py` | MissionProvider lifecycle, protocol, discovery, gadgets, serialization |
| `test_manuscript_variables.py` | token map + live `{{TOKEN}}` cross-reference gate |
| `test_figures.py` | deterministic PNG figures |
| `test_scripts_smoke.py` | subprocess phase-CLI + generator smoke |

Run: `uv run pytest tests/ --cov=src --cov-fail-under=90`. See
`../docs/testing_philosophy.md` for the conventions.
