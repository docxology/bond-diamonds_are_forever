# diamonds-are-forever (CONFLICT STONE · DIAMOND NET) — skills

## When to use

Use when building or maintaining the **diamonds_are_forever** BOND film
package (`projects/working/bond/diamonds_are_forever/`), mission codename
**CONFLICT STONE** (deepening phase **DIAMOND NET**): conflict-diamond
provenance, corridor routing, lot forensics, casino money movement, Benford's
ledger audit, orbital-mirror targeting, and beam-delivery physics.

## Key facts

- Pure domain core (stdlib only, no `bond_api`/`infrastructure`):
  `provenance_chain`, `smuggling_routes`, `lot_forensics`, `casino_network`,
  `benford_audit`, `orbital_mirror`, `beam_physics`.
- Adapter: `src/diamonds_are_forever/mission.py` implements the frozen
  `bond_api` `MissionProvider` (brief/recon/plan/execute/debrief) + a
  `register_gadgets` hook; discovered by slug `diamonds_are_forever`. Its
  public shape is frozen — deepen inside, never break discovery.
- Manifest: `manuscript_variables.py` hydrates every `{{TOKEN}}` from
  `manuscript/config.yaml` + the core (run
  `scripts/z_generate_manuscript_variables.py` for the live count and values);
  `figures.py` renders 7 deterministic PNGs.
- Model constants the manuscript quotes (cutting allowance, density window,
  Benford df/alpha/critical value, strike-irradiance requirement, beam
  scenario) are exported as named constants and cited as tokens — never
  retyped into prose.

## Quick commands

```bash
uv sync --extra dev                                    # install (wires bond-api path dep)
uv run pytest tests/ --cov=src --cov-fail-under=90      # coverage gate
uv run ruff check src/ scripts/ && uv run ruff format src/ scripts/
uv run mypy src/ scripts/
uv run python scripts/generate_figures.py
uv run python scripts/z_generate_manuscript_variables.py
```

## Pitfalls

- Pure core must never import `bond_api`; `mission.py` is the sole adapter.
- Regenerate `output/` (git-ignored) after changes so the tree stays clean.
- Manuscript token cross-reference gate scans only `manuscript/[0-9]*.md`;
  numbered sections must not contain literal `{{...}}` braces.
- No mocks anywhere; deterministic canonical datasets only. Design each
  canonical dataset so its headline metric is forced non-trivial (anomalous
  Benford ledger, flagrant lot, positive routing reduction).
- Keep routing baseline and optimizer in the same graph so `reduction >= 0`.
- Never add a guard that cannot fail (a digit clamp, a cycle de-dup filter, an
  `elif` on an exhausted code set). If the invariant is structural, assert it
  in a test — see `docs/testing_philosophy.md`.
- `benford_audit.first_digit` and `provenance_chain.trace_origin` both have
  non-obvious correct implementations; read *Numerical cautions* in
  `docs/architecture.md` before touching either.
