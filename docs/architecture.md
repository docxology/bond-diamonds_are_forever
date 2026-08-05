# Architecture — diamonds_are_forever (CONFLICT STONE · DIAMOND NET)

How the package is put together: what each module in `src/` computes, how the
pieces compose into one mission, and how `mission.py` satisfies the frozen
`bond-api` `MissionProvider` contract.

## Overview

```
src/diamonds_are_forever/
  provenance_chain.py      pure core — custody graph, break points, coverage, origin
  smuggling_routes.py      pure core — expected-cost corridor routing, survival, reduction
  lot_forensics.py         pure core — weight/density reconciliation audit + verdict
  casino_network.py        pure core — directed weighted transfers, hub, cycles, closure
  benford_audit.py         pure core — leading-digit Benford law + chi-square verdict
  orbital_mirror.py        pure core — occultation, slant range, elevation geometry
  beam_physics.py          pure core — diffraction spot, attenuation, vaporization, min mirror
  mission.py               adapter — MissionProvider (brief/recon/plan/execute/debrief)
  manuscript_variables.py  {{TOKEN}} hydration (config.yaml + pure core)
  figures.py               deterministic figure generation (7 PNGs)
scripts/
  brief.py recon.py plan.py execute.py debrief.py   phase CLIs
  run_mission.py           full flow (+ --json)
  generate_figures.py      renders output/figures/*.png
  z_generate_manuscript_variables.py  hydrates output/manuscript/*
tests/                     deterministic tests, zero mocks
manuscript/                config.yaml + numbered sections ({{TOKEN}}s)
data/claim_ledger.yaml     each headline number and the call that produces it
```

## The seven pure modules

Each is a standalone analysis with its own `canonical_*()` dataset factory, its
own error type, and no knowledge of any other module except where noted.

### `provenance_chain.py`

Models custody as an ordered sequence of `CustodyTransfer` handoffs.
`build_chain` enforces continuity (each handoff's target is the next handoff's
source) and acyclicity. `break_points` returns the indices of `recorded=False`
handoffs; `provenance_coverage` is the documented fraction; `is_conflict_free`
is the all-documented predicate; `trace_origin` slices the actor path from the
chain origin to a named node.

### `smuggling_routes.py`

A directed corridor graph whose edges carry a transport cost and a seizure
probability, with `expected_cost = cost + p * cargo_value`. `least_risk_route`
runs a deterministic Dijkstra over expected cost and returns
`(path, expected_cost, survival)`, where survival is `product(1 - p)` along the
path. `naive_hops_route` is a fewest-hops BFS baseline **in the same graph** —
that shared search space is what makes `route_reduction` provably
non-negative rather than an artefact of a weakened comparator.

### `lot_forensics.py`

Audits per-handoff weight deltas and measured density against three rules:
weight gain (physically impossible for a genuine lot), loss beyond the cutting
allowance (theft), and density outside the diamond window (paste swap). Each
violation is scored by severity, producing an `AuditReport` with a
`clean` / `suspicious` / `flagrant` verdict. The thresholds are exported as
named constants (`CUTTING_LOSS_LIMIT`, `DENSITY_MIN_G_CM3`,
`DENSITY_MAX_G_CM3`, `DIAMOND_DENSITY_G_CM3`, `CANONICAL_LOT_ID`) so the
manuscript can cite them through tokens instead of restating them.

### `casino_network.py`

A directed weighted money graph keyed on `(source, target)`; repeated wires
accumulate onto one edge, as a real ledger must. Surfaces inflow/outflow, net
position, gross flow, the `hub` (greatest gross flow, ties to the
alphabetically first), `find_money_cycles` (DFS back-edge enumeration), and
`laundering_closure` — the share of total flow sitting on any cycle.

### `benford_audit.py`

Tests a ledger's leading digits against `p(d) = log10(1 + 1/d)`, scored by a
Pearson chi-square against the df=8, alpha=0.05 critical value. `first_digit`
reads the digit by exact integer arithmetic — see *Numerical cautions* below
for why the obvious implementations are wrong.

The canonical ledger is a **matched control pair**, because a screen that
fires on every ledger demonstrates nothing:
`legitimate_ledger_amounts()` (80 amounts whose leading digits are the
Fibonacci leading digits, Benford-distributed by theorem — the negative
control, chi-square 0.5258, conforms) plus `laundered_deposit_amounts()`
(61 round-figure deposits, chi-square 83.07, anomalous).
`canonical_ledger_amounts()` concatenates them and scores 35.805, anomalous.
`tests/test_benford_audit.py` asserts all three verdicts, so the baseline
cannot silently stop conforming. Both halves are constructed fixtures: the
pair shows this implementation separates them, not that the screen would
separate real books.

### `orbital_mirror.py`

Geocentric vector geometry for the space mirror. `is_visible` tests whether the
satellite→target ray's nearest approach to Earth's centre dips inside the
sphere (occultation); `slant_range_km` is the straight-line beam distance; and
`elevation_angle_deg` is the angle above the target's local horizon.

### `beam_physics.py`

Chains Airy diffraction, Beer-Lambert attenuation, and the aperture power
budget into `I = S*T*D^4 / (4*1.22^2*lambda^2*R^2)`, then inverts it for
`minimum_mirror_diameter_m` — the smallest mirror meeting a required
irradiance at a given range. `beam_metrics()` returns the canonical bundle the
mission and the manuscript both consume. This is the only pure module that
imports another (it re-uses `SOLAR_CONSTANT_W_M2` from `orbital_mirror`) — a
constant, not behaviour.

## Layer contract

| Layer | Depends on | Import rules |
|---|---|---|
| Pure core (the seven above) | stdlib only (`beam_physics` re-uses an `orbital_mirror` constant) | NO `bond_api`, NO `infrastructure` |
| Adapter (`mission`) | pure core + `bond_api` | sole importer of `bond_api` |
| Manifest/figures | pure core + `yaml` / `matplotlib` | reads `manuscript/config.yaml` |
| Scripts | adapter / core | thin orchestration only |

The pure core is deliberately infrastructure-free so it stays importable even
if the `bond-api` path dependency is ever unavailable (a stated fallback).

## How `mission.py` implements the frozen MissionProvider

`bond-api` defines `MissionProvider` as a Protocol: a `film` attribute plus
five lifecycle methods, each returning a specific frozen dataclass. **This
public shape is frozen across the suite** — `bond-cli`, the coordinator's
reconcile pass, and the orchestrator all consume it, so deepening happens
inside the method bodies, never in their signatures.

| Protocol member | Returns | What this package does |
|---|---|---|
| `film` | `str` | Class attribute `"diamonds_are_forever"` — the slug discovery resolves. |
| `brief()` | `MissionBrief` | Declares six objectives and six `Asset`s (custody chain, corridor network, lot samples, casino network, ledger, satellite), each sized by calling the matching `canonical_*()` factory, plus two `Constraint`s (determinism, provenance). |
| `recon(ReconRequest)` | `ReconReport` | Surveys every domain and emits one `Finding` per concept plus a `goal` finding echoing the request. Read-only. |
| `plan(MissionBrief)` | `MissionPlan` | One `Step` per concept (seven), each parameterised by the size of its canonical dataset. |
| `execute(MissionPlan)` | `MissionOutcome` | Runs all seven analyses, assembles the nested `results` dict, and attaches a `Provenance` block: package version, seed 7, `wall_time_s = 0.0`, and the SHA-256 `input_hash`. |
| `debrief(MissionOutcome)` | `Debrief` | Reads only `outcome.results` — never recomputes — and formats eight standing lessons from those values. |

Two module-level surfaces sit alongside the class and are equally frozen:

- **`register_gadgets(registry)`** publishes eleven named callables under the
  slug: `provenance.break_points`, `provenance.coverage`, `provenance.origin`,
  `smuggling.route`, `smuggling.reduction`, `forensics.audit`, `casino.hub`,
  `casino.closure`, `benford.report`, `orbital.visible`, `beam.metrics`. The
  registry is the Q-branch lookup other packages use, so the gadget *names* are
  part of the contract, not an implementation detail.
- **`mission_input_hash()`** serialises every canonical input to sorted JSON
  and returns its SHA-256. Any change to any dataset changes the hash, so an
  outcome can be audited without re-running the mission.

## Data flow

1. Frozen canonical datasets live as `canonical_*()` factories in each pure
   module (single source of truth).
2. The adapter calls them during `execute()` to compute `results` and the
   `input_hash`.
3. `manuscript_variables.generate_variables()` calls the *same* factories to
   compute `{{TOKEN}}` values — so the manuscript and the mission outcome
   cannot disagree.
4. `figures.py` renders the same data to `output/figures/`.

Model constants the manuscript quotes (cutting allowance, density window,
Benford critical value and df/alpha, the strike-irradiance requirement, the
beam scenario geometry) are exported as named constants and reach the prose as
tokens. No literal number is written into a manuscript section.

## Determinism

- No RNG anywhere; the mission seed is a constant (7).
- `Provenance.wall_time_s` is always 0; input fingerprints are SHA-256 over the
  sorted JSON of canonical inputs.
- Corridor adjacency lists and casino names are sorted; the Dijkstra heap
  tie-breaks on a monotonic insertion counter, so equal-cost paths resolve the
  same way on every run.

## Numerical cautions

Two places where the obvious implementation is silently wrong. Both are fixed,
and both are pinned by regression tests — read these before touching either
function.

- **`benford_audit.first_digit`** must not scale iteratively.
  `while m < 1.0: m *= 10.0` re-rounds on every step, so error compounds across
  the exponent range: `1e-300` drifts to a mantissa of `9.999999999999993` and
  reports a 9 instead of a 1. Formatting with `%e` is also wrong — it *rounds*,
  and Benford's law is defined on truncation. The module uses exact integer
  arithmetic on `as_integer_ratio()`, cross-checked in tests against an
  independent `Decimal` oracle across the whole double exponent range.
- **`provenance_chain.trace_origin`** cannot use a scan-and-break to reach the
  origin: the origin is never any handoff's `target` in an acyclic chain, so
  the break never fires and the function returned the *entire* chain. It slices
  to the first arrival instead, with the origin handled as an explicit early
  return.

Related discipline: this package carries no branch that cannot fire. A
dead-but-plausible guard (a digit clamp, a cycle de-duplication filter, a
fourth `elif` on a three-valued code) reads as safety while testing nothing, so
where the invariant is structural it is asserted in a test rather than guarded
in the code.
