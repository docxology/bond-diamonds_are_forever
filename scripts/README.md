# scripts/ — diamonds_are_forever (CONFLICT STONE)

Thin orchestrators for the BOND film package. All business logic lives in
`src/diamonds_are_forever/`; each script bootstraps `src/` onto `sys.path` and
forwards to the core or the mission adapter.

## Phase CLIs

| Script | Phase | Prints |
|---|---|---|
| `brief.py` | brief | objectives, assets, constraints |
| `recon.py` | recon | survey findings across the three domains |
| `plan.py` | plan | analytic steps |
| `execute.py` | execute | outcome results + provenance |
| `debrief.py` | debrief | outcome success + lessons |
| `run_mission.py` | all | full flow; `--json` emits round-trip `MissionOutcome` |

## Generators

| Script | Produces |
|---|---|
| `generate_figures.py` | `output/figures/{provenance_chain,casino_network,orbital_visibility}.png` |
| `z_generate_manuscript_variables.py` | `output/data/manuscript_variables.json` + hydrated `output/manuscript/` |

Run from the package root: `uv run python scripts/<name>.py`.
