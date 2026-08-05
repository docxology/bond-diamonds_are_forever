# diamonds_are_forever — AGENTS.md

BOND film package **Diamonds Are Forever (1971)** · mission codename **CONFLICT
STONE** (deepening phase **DIAMOND NET**). One package in the PROJECT BOND
suite at `projects/working/bond/` (local-only working tree, no remote).

## Scope & guardrails

- **Scope is exactly this directory.** Never touch sibling bond packages, bond
  root files, or the template repo.
- **Local-only.** There is no remote; never push.
- **Path-scoped commits**: `git add -A` inside this repo only.
- **No mock framework.** Real data + computation only.
- **≥90% line+branch coverage** on `src/`.
- **Deterministic**: fixed canonical datasets, fixed seed, no untracked RNG, no
  wall-clock in persisted artifacts. The manuscript edition stamp comes from
  `paper.date` in `manuscript/config.yaml`, never from `datetime.now`;
  `tests/test_manuscript_variables.py::test_regeneration_is_byte_identical_across_a_second_boundary`
  regenerates twice across a second boundary and diffs the bytes.
- **Thin orchestrators** in `scripts/`; business logic in `src/`.
- **No number is hand-authored in manuscript prose** — see *Manuscript* below.

## Build

```bash
uv sync --extra dev     # from this directory; wires the bond-api path dependency
```

`uv sync --extra dev` must run before pytest: the tests exercise the real
`bond_api` protocol, and `mission.py` imports it.

## Test & verify

Run all four; all four must be clean before you claim done.

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

Then confirm the tree is consistent and the lineage is clean:

```bash
uv run python scripts/generate_figures.py                  # 7 PNGs under output/figures/
uv run python scripts/z_generate_manuscript_variables.py    # strict: unresolved {{TOKEN}} fails
rg -n "template[_]code_project"                             # must be zero hits
git status                                                  # must be clean after committing
```

`z_generate_manuscript_variables.py` is strict by default — a manuscript
section containing a token that `generate_variables()` does not produce fails
the run rather than emitting raw braces. `--allow-draft` bypasses this and is
for intentional early drafts only.

Run the mission itself to sanity-check end to end:

```bash
uv run python scripts/run_mission.py          # brief -> recon -> plan -> execute -> debrief
uv run python scripts/run_mission.py --json   # round-trip serialized outcome
```

Two runs must print the same input hash. If they do not, something introduced
non-determinism.

## Layer contract

| Surface | Rule |
|---|---|
| `src/diamonds_are_forever/{provenance_chain,smuggling_routes,lot_forensics,casino_network,benford_audit,orbital_mirror,beam_physics}.py` | Pure domain core — stdlib math only, **no** `bond_api`/`infrastructure` imports; importable standalone. `beam_physics` may import the `SOLAR_CONSTANT_W_M2` constant from `orbital_mirror`; nothing else crosses. |
| `src/diamonds_are_forever/mission.py` | Thin adapter — implements the frozen `bond_api.protocol.MissionProvider` and registers gadgets. Public shape frozen. |
| `src/diamonds_are_forever/manuscript_variables.py`, `figures.py` | Manifest/figures over the pure core |
| `scripts/` | Thin CLIs (brief/recon/plan/execute/debrief, run_mission, figure + manuscript-variable generators) |

## Protocol integration (frozen — do not reshape)

- Depends on `bond-api` via `[tool.uv.sources]` path dependency.
- `mission.py` exposes `MissionProvider` at module top level under that exact
  name, so the orchestrator discovers it by slug `diamonds_are_forever` via
  `bond_api.discovery`.
- Frozen: the `film` attribute, the five lifecycle methods and their return
  dataclasses, `register_gadgets`, and the eleven gadget **names**. `bond-cli`,
  the coordinator reconcile, and the orchestrator all consume these. Deepen
  inside the methods; never change a signature or rename a gadget.
- The pure core stays importable without `bond-api` (a stated fallback).

## Manuscript

Metrics flow from `manuscript/config.yaml` + `src/.../manuscript_variables.py`
into `{{TOKEN}}`s. Never write a number into a section file. This covers model
constants too — thresholds, critical values, and requirements are exported as
named constants from their owning module and cited as tokens.

Adding a quantitative claim means three edits together: the variable in
`manuscript_variables.py`, the token in the section, and the expected-key set
in `tests/test_manuscript_variables.py`.

## Reference files

- `docs/README.md` — documentation index.
- `docs/agent_instructions.md` — operational constraints, the frozen surface,
  and the pre-change checklist.
- `docs/architecture.md` — module-by-module design, the `MissionProvider`
  mapping, and two numerical traps. Read before altering `src/`/`scripts/`.
- `docs/testing_philosophy.md` — before writing/modifying `pytest` files.
- `manuscript/SYNTAX.md` — manuscript token + figure protocol.
- `data/claim_ledger.yaml` — headline claims and the calls producing them.
