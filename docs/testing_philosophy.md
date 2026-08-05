# Testing Philosophy — diamonds_are_forever (CONFLICT STONE)

The suite is **deterministic, coverage-gated, and mock-free**. Tests are real
computations over the frozen canonical datasets and the real BOND-API protocol.

## Principles

1. **No mocks.** Never `unittest.mock` / `mocker.patch` / `MagicMock`
   /`create_autospec`. A "double" is only ever the real canonical dataset or a
   real `tmp_path` directory.
2. **Real protocol.** The mission tests exercise the actual `bond_api`
   `MissionProvider` protocol (discovery, `run_mission`, serialization), never
   a stand-in.
3. **Deterministic.** Fixed inputs, fixed seed, no RNG, no wall-clock
   assertions. Many tests assert byte/structural identity across calls.
4. **Coverage-gated.** `uv run pytest tests/ --cov=src --cov-fail-under=90`
   must pass (line + branch).

## File map

| Test file | Covers |
|---|---|
| `test_provenance_chain.py` | custody graph, break points, coverage, origin, validation errors |
| `test_smuggling_routes.py` | expected-cost Dijkstra routing, BFS baseline, survival, reduction |
| `test_lot_forensics.py` | weight-gain / excess-loss / density-mismatch rules, verdicts |
| `test_casino_network.py` | transfers, hub, cycles, laundering closure, validation errors |
| `test_benford_audit.py` | leading-digit law, chi-square, report verdict, validation errors |
| `test_orbital_mirror.py` | occultation, slant range, elevation, beam power, validation errors |
| `test_beam_physics.py` | diffraction spot, Beer-Lambert, vaporization, min-mirror inversion |
| `test_mission.py` | MissionProvider lifecycle, protocol check, discovery, gadgets, serialization |
| `test_manuscript_variables.py` | token map + live `{{TOKEN}}` cross-reference gate |
| `test_figures.py` | deterministic PNG output (7 figures) |
| `test_scripts_smoke.py` | subprocess runs of every phase CLI + generators |

## Pattern notes

- **Validation branches** are hit explicitly (empty/out-of-range/non-number
  inputs) to keep branch coverage high.
- **Determinism proofs**: call a function twice and compare; run the full
  mission twice and compare `Provenance.input_hash` and `Debrief.lessons`.
- **Manuscript token gate**: `test_live_token_cross_reference` scans
  `manuscript/[0-9]*.md` (numbered sections only) and asserts every `{{TOKEN}}`
  resolves through `generate_variables()`. Guide files (`SYNTAX.md`,
  `AGENTS.md`) legitimately show literal braces and are excluded.
- **Subprocess smoke** runs scripts with `sys.executable`, `cwd=<package root>`,
  asserting exit code 0 and expected stdout/artifact presence.
