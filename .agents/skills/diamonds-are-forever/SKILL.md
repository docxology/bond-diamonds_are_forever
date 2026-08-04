# diamonds-are-forever (CONFLICT STONE) — skills

## When to use

Use when building or maintaining the **diamonds_are_forever** BOND film
package (`projects/working/bond/diamonds_are_forever/`), mission codename
**CONFLICT STONE**: conflict-diamond provenance, Las Vegas casino money
movement, and orbital-mirror targeting geometry.

## Key facts

- Pure domain core: `src/diamonds_are_forever/{provenance_chain,casino_network,orbital_mirror}.py`
  (stdlib only, no `bond_api`/`infrastructure`).
- Adapter: `src/diamonds_are_forever/mission.py` implements the frozen
  `bond_api` `MissionProvider` (brief/recon/plan/execute/debrief) and registers
  gadgets; discovered by slug `diamonds_are_forever`.
- Manifest: `manuscript_variables.py` hydrates `{{TOKEN}}`s from
  `manuscript/config.yaml` + the core; `figures.py` renders deterministic PNGs.

## Quick commands

```bash
uv sync --extra dev                                    # install (wires bond-api path dep)
uv run pytest tests/ --cov=src --cov-fail-under=90      # coverage gate
uv run ruff check src/ scripts/ && uv run ruff format src/ scripts/
uv run mypy src/ scripts/
uv run python scripts/run_mission.py --json             # full flow
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Pitfalls

- Pure core must never import `bond_api`; `mission.py` is the sole adapter.
- Regenerate `output/` (git-ignored) after changes so the tree stays clean.
- The manuscript token cross-reference gate scans only `manuscript/[0-9]*.md`;
  guide files may show literal `{{TOKEN}}` braces but numbered sections must not.
- No mocks anywhere; deterministic canonical datasets only.
