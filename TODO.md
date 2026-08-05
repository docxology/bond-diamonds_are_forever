# diamonds_are_forever — CONFLICT STONE · DIAMOND NET TODO

Forward-only backlog for the BOND film package **Diamonds Are Forever (1971)**.
For what the package *is*, see `README.md`; for how it is built, see
`docs/architecture.md`. This file tracks only what is left.

## Remaining work

1. **Provenance-export CLI.** Write canonical inputs + the mission outcome to a
   single JSON artifact under `output/data/`. This is the feed for the
   bond-utilities integration point below, and the only reason it is not built
   yet is that the consuming API is not fixed.
2. **Satellite strike scheduling.** A dynamic pass over `beam_physics`:
   allocate dwell time across the visible target set under an energy budget,
   given that each strike needs `time_to_vaporize_s` at the delivered
   irradiance. The physics is in place; the scheduler is not.
3. **Spectroscopy channel for lot forensics.** `lot_forensics` currently
   separates paste from diamond on density alone. A second, independent
   channel (refractive index or thermal conductivity, both standard gemological
   discriminators) would make the substitution finding two-instrument rather
   than one.
4. **Cargo-value sensitivity.** `route_reduction` is reported at a single cargo
   value. The optimum route flips to the fewest-hops baseline as cargo value
   falls toward zero — sweeping the crossover point would be a more honest
   result than the single figure.

## Declared integration points

- **bond-api protocol (FROZEN)** — implemented. `mission.py` adapts the frozen
  `MissionProvider` contract; public shape unchanged across the deepening
  phase. No further work.
- **bond-utilities provenance** — *not yet consumed*. When bond-utilities
  ships, delegate outcome persistence to
  `bond_utilities.mission_io.record_provenance_outcome`. Until then the package
  keeps its own SHA-256 `mission_input_hash()`; binding later needs no rework,
  only a call-site change.
- **orchestrator discovery** — done. `mission.py` exposes `MissionProvider` at
  module top level under the stable name; the orchestrator resolves the slug
  `diamonds_are_forever` via `bond_api.discovery`.

## Not planned

- Re-wiring this tree into the monorepo pipeline. It is standalone and
  local-only by design; `docs/_generated/` equivalents are out of scope unless
  that changes.
- Orbital mechanics, beam-riding control, adaptive optics, or thermal blooming
  in `beam_physics`. The scope note in
  `manuscript/07_scope_and_related_work.md` states these omissions explicitly,
  and the minimum mirror diameter is presented as a lower bound because of
  them. Adding one would mean revising that claim.

## Verification

Gates are defined in `AGENTS.md` and `domain_profile.yaml`; run them rather
than trusting a number recorded here. The standing bar: `pytest` with
`--cov-fail-under=90` on `src/`, ruff `check` + `format --check`, mypy, all
clean, zero mocks, zero skips, and a clean `git status` after committing.
