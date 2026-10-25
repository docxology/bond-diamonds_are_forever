# TODO — diamonds_are_forever (CONFLICT STONE · DIAMOND NET)

Special-agent mission software for the BOND film package *Diamonds Are Forever
(1971)*: seven pure analytic modules (provenance chain, smuggling corridors, lot
forensics, casino network, Benford ledger audit, orbital targeting, beam
physics) behind a frozen `bond-api` `MissionProvider` adapter. For what it *is*,
read `README.md`; for how it works, `docs/architecture.md`. This file tracks only
what is left.

**Verified state, re-measured 2026-08-05 in this tree after the C1 fix:**
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **234 passed**,
**100.00%** line+branch coverage on `src/` (all ten measured modules at 100%;
`*/__init__.py` is omitted by `pyproject.toml:47-51`). `ruff check`,
`ruff format --check`, and `mypy src/ scripts/` are clean, the
`template[_]code_project` lineage grep is empty, and `git status` is clean.
The single unresolved item from the adversarial audit
(`output/verify/diamonds_are_forever.unresolved.json`) is a scope note, not a
defect — it is recorded under *Known limitations* below.

**Round-2 verified state, re-measured 2026-08-06:** `uv run pytest tests/
--cov=src --cov-fail-under=90` → **251 passed, 100.00%** line+branch coverage on
`src/`, 0 skipped, 0 failed (coverage restored to 100% after the round-2
additions; the completeness-reference corpus now covers every branch of the
Johnson enumerator). `ruff check`, `ruff format --check`, and `mypy` are clean;
the mission input hash is deterministic across runs
(`0a6e93ab…`); 8 figures and 63 manuscript tokens hydrate; the
`template[_]code_project` lineage grep shows only intentional doc
self-references. See the *Round-2 (2026-08-06)* section at the end of this file.

---

## Open work

Ordered by priority within each group. Every item names the file, what "done"
looks like, and the command that closes it. Nothing here has been started.

### Correctness

#### ~~C1 — Manuscript hydration is not byte-deterministic, and four documents claim it is~~ — CLOSED 2026-08-05

**Resolution: the claim was made true.** `GENERATION_TIMESTAMP` is gone. The
manuscript is now stamped `MANUSCRIPT_DATE`, read from `paper.date` in
`manuscript/config.yaml` by `manuscript_variables.pinned_manuscript_date()` — a
committed input, not a clock; a config with no `date` raises rather than falling
back to `datetime.now`. `manuscript/05_experimental_setup.md`,
`manuscript/SYNTAX.md`, `manuscript/06_reproducibility.md`, `AGENTS.md`,
`STANDALONE.md`, `README.md` and `docs/agent_instructions.md` were updated to
state the property precisely, naming `PYTHON_VERSION` as the one token still
read from the machine (so byte-identity is claimed for reruns on the same
interpreter).

Bound by `tests/test_manuscript_variables.py::test_regeneration_is_byte_identical_across_a_second_boundary`,
which runs the real orchestrator twice into two temp trees — separated by a
sleep past the next whole second, so a seconds-resolution clock cannot match by
luck — and diffs the SHA-256 of every written file, after asserting the trees
are non-empty. Proven failable: temporarily restoring
`datetime.now(timezone.utc)` turned it red on
`['data/manuscript_variables.json', 'manuscript/05_experimental_setup.md']`, and
green again on restore. The two-run `md5` of `output/**/*.{json,md}` now matches
(`1675efd56a35143f4991a10e27d4ed00` twice, 2 s apart).

<details><summary>Original finding</summary>

`manuscript_variables.py:175` sets
`"GENERATION_TIMESTAMP": datetime.now(timezone.utc).isoformat(...)`. That value
is written into two persisted artifacts — `output/data/manuscript_variables.json`
and, via `{{GENERATION_TIMESTAMP}}` in `manuscript/05_experimental_setup.md:44`,
into `output/manuscript/05_experimental_setup.md`. Two runs seconds apart differ:

```
< "GENERATION_TIMESTAMP": "2026-08-05T19:43:06+00:00"
> "GENERATION_TIMESTAMP": "2026-08-05T19:43:08+00:00"
```

Four documents assert the opposite: `AGENTS.md:16` ("no wall-clock in persisted
artifacts"), `docs/agent_instructions.md:17` (same, plus "Re-running produces
byte-identical output"), `STANDALONE.md:24`, and
`manuscript/06_reproducibility.md:6` ("no wall-clock dependence in any persisted
artifact"). The mission outcome itself *is* clean (`mission.py:389` pins
`wall_time_s=0.0`); the manuscript pipeline is not.

**Done:** either the timestamp is removed/pinned (a `SOURCE_DATE_EPOCH`-style
override, or `paper.date` from `manuscript/config.yaml:10`) so hydration is
byte-reproducible, or all four claims are narrowed to name the timestamp as the
one deliberate exception. Whichever is chosen, a test must pin it.

**Command:**
```bash
uv run python scripts/z_generate_manuscript_variables.py && cp output/data/manuscript_variables.json /tmp/mv1.json \
  && uv run python scripts/z_generate_manuscript_variables.py && diff /tmp/mv1.json output/data/manuscript_variables.json
```
(exit 0 = closed, if the byte-identity route is taken.)

</details>

#### C2 — The `bond-api` dependency is an absolute machine path

`pyproject.toml:35`:

```toml
bond-api = { path = "/Users/4d/Documents/GitHub/template/projects/working/bond/bond-api" }
```

`STANDALONE.md` calls this a standalone package that another operator can clone
and `uv sync`. With an absolute path baked in, relocating or copying the bond
tree breaks `uv sync --extra dev`, and every test in `tests/test_mission.py`
(which imports `bond_api` for real) fails at collection. The sibling layout is
already fixed by the suite, so `{ path = "../bond-api" }` expresses the same
dependency without pinning one machine.

**Done:** the `[tool.uv.sources]` entry is relative, and `uv sync --extra dev`
plus the full suite pass from a copy of the bond tree at a different path.

**Command:**
```bash
cp -R ../../bond "$TMPDIR/bondcopy" && cd "$TMPDIR/bondcopy/diamonds_are_forever" \
  && uv sync --extra dev && uv run pytest tests/ -q
```

#### C3 — `find_money_cycles` is cited as elementary-circuit enumeration, but is a back-edge DFS

`casino_network.py:98-134` reports one cycle per DFS back edge. That is not the
elementary-circuit enumeration of Tarjan (1973), which
`manuscript/07_scope_and_related_work.md:27-29` and `manuscript/99_references.md:41`
attach to it ("Cycle detection is the elementary-circuit enumeration problem
[@tarjan1973] restricted to the small canonical graph").
`manuscript/02_methodology.md:45-48` repeats the citation. Concrete miss —
a graph where a circuit re-enters an already-finished node:

```python
edges = [("a","b"), ("a","c"), ("b","d"), ("c","d"), ("d","a")]
# find_money_cycles() -> (('a','b','d','a'),)   # ('a','c','d','a') is never reported
# laundering_closure() -> 0.6                    # every edge is on a circuit; the truth is 1.0
```

The canonical network (three edge-disjoint loops) is unaffected — it really does
have exactly three circuits and the DFS finds all three — so no published number
changes. The defect is the general claim, and the under-reporting of
`laundering_closure` on any graph with overlapping circuits.

**Done:** either the enumerator becomes complete (Johnson 1975 / Tarjan 1973), or
the docstring and both manuscript sections state that this is back-edge cycle
*detection* rather than circuit *enumeration* — and the counterexample above is
pinned as a test so the boundary cannot be forgotten.

**Command:** `uv run pytest tests/test_casino_network.py -v` (the new
counterexample test must exist and pass), then
`rg -n "tarjan1973" manuscript/` and check each surviving citation matches the
implemented behaviour.

### Verification

Claims that are true today (each checked by hand this session) but that no test
can fail on.

#### V1 — 15 of the 21 rows in `data/claim_ledger.yaml` are unbound

`tests/test_benford_audit.py:306-327` recomputes the six `benford.*` rows against
the core. Nothing checks the other fifteen: `provenance.*` (`claim_ledger.yaml:7-15`),
`smuggling.*` (`:16-30`), `forensics.*` (`:31-36`), `casino.*` (`:37-42`), and
`beam.*` (`:64-72`). All fifteen are accurate as of this session (recomputed:
5 / 2 / 0.6, 10 corridors, 9.35 M, 0.3444 survival, 0.1614 reduction, 2 anomalies
flagrant, 7 casinos, 0.7742 closure, 0.564 m spot, 564.6×, 42.7 m) — but they are
stored rows that can silently decay the moment a canonical dataset moves.

**Done:** every `claims:` row is recomputed from its named `source:` call and
compared, in one test that iterates the file rather than hard-coding ids, so a
new row cannot be added unbound.

**Command:** `uv run pytest -k claim_ledger -v` (must collect a test that covers
all 21 ids; assert the count).

#### V2 — The beam scenario's slant range is a hand-copied literal of the geometry

`beam_physics.py:61` declares `slant_range_km: float = 36_998.4` with the comment
`# mirror -> Washington DC at GEO`, and `tests/test_beam_physics.py:40` pins that
same literal. The value that actually falls out of the geometry module is
`orbital_mirror.slant_range_km(canonical_satellite(), GroundTarget("Washington DC", 38.90, -77.04))`
= **36998.402**. Nothing binds one to the other: change the satellite altitude in
`orbital_mirror.canonical_satellite()` (`orbital_mirror.py:209-211`) or a target
coordinate and the beam scenario keeps the stale range while the test still
passes — the headline `BEAM_MIN_MIRROR_DIAMETER_M` would then be computed at a
range the mission no longer uses.

**Done:** a test asserts `canonical_beam_scenario().slant_range_km ==
pytest.approx(slant_range_km(canonical_satellite(), <the DC target>), abs=0.01)`,
so the literal is checked against its source of truth rather than against itself.

**Command:** `uv run pytest tests/test_beam_physics.py -k slant -v`

#### V3 — The package version exists in four places with nothing tying them together

`pyproject.toml:11`, `src/diamonds_are_forever/__init__.py:39`,
`src/diamonds_are_forever/mission.py:53` (`PACKAGE_VERSION`, the value that goes
into the `Provenance` block), and `manuscript/config.yaml:9` (the value that
becomes `{{CONFLICT_VERSION}}`) all say `"0.1.0"` independently.
`manuscript/06_reproducibility.md:9-10` says the mission outcome carries "a
package version ({{CONFLICT_VERSION}})" — but that token is read from the YAML
config, not from the provenance block it describes. They agree today by
coincidence of editing.

**Done:** one test asserts all four strings are equal (reading `pyproject.toml`
with `tomllib`), so a version bump in one place fails the suite.

**Command:** `uv run pytest -k version -v`

#### V4 — The manuscript token gate is one-directional

`tests/test_manuscript_variables.py:177-184` asserts `used - generated == ∅`
(a section may not cite an unknown token) but never `generated - used`. Measured
this session: 63 generated, 63 used, **0 orphans** — so nothing is wrong today,
and nothing stops a variable from being computed, exported, and cited nowhere,
or a token from being quietly deleted from prose while its variable lingers.

**Done:** the same test also asserts `set(variables) - used_across_all_sections`
is empty (or an explicit, justified allow-list).

**Command:** `uv run pytest tests/test_manuscript_variables.py -k cross_reference -v`

#### V5 — "The pure core is importable without `bond-api`" is asserted in six documents and tested nowhere

The fallback is claimed in `README.md:56-58`, `AGENTS.md:68` and `AGENTS.md:83`,
`STANDALONE.md:22-23`, `docs/agent_instructions.md:28-30`,
`docs/architecture.md:119-120`, and `src/diamonds_are_forever/__init__.py:8`.
It holds today — verified by hand with a `sys.meta_path` blocker: all seven pure
modules plus `manuscript_variables` and `figures` import cleanly with `bond_api`
unavailable, and only `mission` raises `ImportError`. But the guarantee is one
stray top-level import away from being false, and the suite always runs with
`bond-api` installed, so it would never notice.

**Done:** a test spawns a subprocess that installs a `sys.meta_path` finder
raising `ImportError` for `bond_api`, imports each of the seven pure modules, and
asserts `mission` is the *only* module that fails.

**Command:** `uv run pytest -k pure_core -v`

#### V6 — Figure tests assert only that a PNG exists

`tests/test_figures.py:29-32` (`_assert_png`) checks `is_file()`, non-zero size,
and the `\x89PNG` magic bytes. A figure that plotted the wrong series, dropped a
data set, or rendered blank axes would pass all eight tests, and `figures.py` is
at 100% coverage regardless — executed is not correct. Renders *are* byte-stable
run to run (measured: identical SHA-256 for all seven PNGs across two separate
output directories), but no test asserts that either.

**Done:** each figure test binds at least one datum from the pure core to the
rendered artifact (e.g. the Benford figure's bar heights equal
`benford_report(canonical_ledger_amounts()).distribution`; the beam figure's
marked requirement equals `REQUIRED_STRIKE_IRRADIANCE_W_M2`) — most cheaply by
having the generators return the `Figure` alongside the path, or by asserting on
the artists before `savefig`. Plus one byte-identity test across two renders.

**Command:** `uv run pytest tests/test_figures.py -v`

#### V7 — The `experiment_plan.yaml` baseline/ablation rows are unbound prose

The file's own comment (`experiment_plan.yaml:24-30`) records that the
`benford_ledger` baseline/ablation rows were once *wrong* and are now enforced by
`tests/test_benford_audit.py`. The other two ablation rows are not enforced:
`lot_forensics` ("remove density probe -> only excessive-loss anomaly remains",
`:20`) and `smuggling_corridors` ("single corridor chain -> reduction collapses
to 0", `:15`). Both are true today — checked by hand: widening the density window
leaves exactly one `excessive_loss` anomaly (verdict `suspicious`), and a
two-hop single-path chain gives `route_reduction` exactly `0.0` — but the same
class of decay that produced the Benford defect applies to them verbatim.

**Done:** one test per ablation row, recomputing the stated ablation and
asserting the stated outcome.

**Command:** `uv run pytest tests/test_lot_forensics.py tests/test_smuggling_routes.py -k ablation -v`

### Documentation

#### D1 — The Airy encircled-energy assumption is not listed among the model's omissions

`beam_physics.delivered_irradiance_w_m2` (`beam_physics.py:118-129`) divides the
*entire* captured power by the area of the first-null disk. The real Airy pattern
puts ≈83.8% of the power inside the first null, so delivered irradiance is
≈1.19× optimistic and `minimum_mirror_diameter_m` is ≈4.6% small.
`manuscript/07_scope_and_related_work.md:36-42` lists the omissions (orbital
mechanics, beam-riding control, adaptive optics, thermal blooming, material
science beyond one fluence) and concludes the minimum diameter is "a lower bound
on the real requirement" — the direction is right, and this assumption pushes the
same way, so no claim is falsified. It is simply the largest unnamed one.

**Done:** the omission list names the full-power-inside-the-first-null assumption
alongside the others, and the module docstring (`beam_physics.py:1-20`) says the
same.

**Command:** `rg -n "encircled|first null" manuscript/07_scope_and_related_work.md src/diamonds_are_forever/beam_physics.py`
(must return hits in both).

#### D2 — `tests/PATTERNS.md` names a class that does not exist

`tests/PATTERNS.md:20` shows `OrbitalsSatellite(altitude_km=-1.0, ...)`. The class
is `orbital_mirror.Satellite`. Anyone copying the validation-branch pattern gets a
`NameError`.

**Done:** the snippet names `Satellite` (with its import), and the pattern file
carries no other symbol that `rg` cannot find in `src/`.

**Command:** `uv run python -c "from diamonds_are_forever.orbital_mirror import Satellite"`
and `rg -n "Orbitals" tests/` (must be empty).

### Extension

Genuine future work — nothing here is wrong today.

#### E1 — Provenance-export CLI

Write the canonical inputs plus the mission outcome to a single JSON artifact
under `output/data/`. `scripts/run_mission.py --json` currently only prints to
stdout, so nothing persists the outcome next to
`output/data/manuscript_variables.json`. This is the feed for the bond-utilities
integration below; it is unbuilt only because the consuming API is not fixed.
**Done:** a script writes the artifact, `domain_profile.yaml`'s
`artifact_expectations` lists it, and a smoke test asserts it round-trips through
`bond_api.serialization`.

#### E2 — Satellite strike scheduling

A dynamic pass over `beam_physics`: allocate dwell time across the visible target
set (`orbital_mirror.canonical_targets()`) under an energy budget, given each
strike needs `time_to_vaporize_s` at the delivered irradiance. The physics is
complete (`beam_physics.py:139-145`); no scheduler exists.
**Done:** a pure function returning a deterministic schedule, with a test showing
the budget binds (an infeasible budget must drop a target, not silently
over-allocate).

#### E3 — Second forensic channel for lot forensics

`lot_forensics.py` separates paste from diamond on density alone
(`DENSITY_MIN_G_CM3` / `DENSITY_MAX_G_CM3`, `lot_forensics.py:42-44`). A second
independent channel — refractive index or thermal conductivity, both standard
gemological discriminators — would make the substitution finding two-instrument
rather than one, and would let `03_results.md:43-45` claim independence of the
*substitution* finding rather than of the substitution-vs-theft pair.
**Done:** a second channel with its own constants and its own anomaly code, and a
test where the two channels disagree.

#### E4 — Cargo-value sensitivity sweep

`route_reduction` (`smuggling_routes.py:224-228`) is reported at a single cargo
value (5.0 M USD, `smuggling_routes.py:231-233`). As cargo value falls toward
zero the optimum collapses onto the fewest-hops baseline and the reduction goes
to 0; sweeping the crossover is a more honest result than one figure.
**Done:** a sweep function plus a figure, and a test asserting monotonicity of
reduction in cargo value across the sweep (with the crossover located, not
assumed).

## Declared integration points

- **bond-api protocol (FROZEN)** — implemented. `mission.py` adapts the frozen
  `MissionProvider` contract; the public shape is unchanged across the deepening
  phase. No work remaining.
- **orchestrator discovery** — done. `mission.py` exposes `MissionProvider` at
  module top level under the stable name; the orchestrator resolves the slug
  `diamonds_are_forever` via `bond_api.discovery`
  (exercised by `tests/test_mission.py:7`).
- **bond-utilities provenance** — *not yet consumed*. When bond-utilities ships,
  delegate outcome persistence to
  `bond_utilities.mission_io.record_provenance_outcome`. Until then the package
  keeps its own SHA-256 `mission_input_hash()` (`mission.py:62`); binding later
  needs a call-site change, not rework. Blocks nothing; see E1.

---

## Known limitations (not bugs)

Accepted and deliberate. Recorded here so they are not re-litigated as defects.

- **The Benford result is a specificity check on two constructed fixtures, not a
  detection rate.** This is the one unresolved entry in
  `output/verify/diamonds_are_forever.unresolved.json`. Both halves of the
  canonical ledger — the Fibonacci-derived negative control
  (`benford_audit.py:207-226`) and the round-figure deposits (`:229-247`) — are
  designed, not empirical. What is established is that this implementation
  separates *these two halves*; no false-positive or false-negative rate is
  estimated, and none can be read off it. The honest scope is stated in
  `manuscript/03_results.md:88-91`, `manuscript/02_methodology.md:76-78`, the
  `benford_audit` module docstring (`:27-30`), and `docs/architecture.md:88-91`.
  Closing this would mean sourcing real ledgers, which is out of scope for a
  self-contained package.
- **The Benford test is a screen, not a proof of laundering.**
  `manuscript/07_scope_and_related_work.md:33-35` says so explicitly.
- **The beam model omits orbital mechanics, beam-riding control, adaptive optics,
  thermal blooming, and material science beyond a single vaporization fluence.**
  Every omission pushes the same direction, which is why the minimum mirror
  diameter is presented as a *lower bound* rather than an estimate
  (`manuscript/07_scope_and_related_work.md:36-42`). Adding any one of them means
  revising that claim, not just the number. (D1 above is about *naming* one more
  omission, not removing it.)
- **The canonical datasets are small and illustrative.** Five handoffs, ten
  corridors, seven casinos, 141 ledger transactions, three targets. They are
  chosen so each headline metric is non-trivial rather than vacuous
  (`manuscript/06_reproducibility.md:19-24`); they are not samples of anything.
- **This tree is standalone, and published on its own.** `origin` is
  `github.com/docxology/bond-diamonds_are_forever`; there are no
  `docs/_generated/` equivalents and no monorepo pipeline. Re-wiring it into
  one is out of scope unless that changes. (C2 is about the *dependency path*,
  not about this.)
- **Coverage omits `*/__init__.py`** (`pyproject.toml:47-51`).
  `src/diamonds_are_forever/__init__.py` is a docstring plus `__version__`,
  `FILM`, and `CODENAME` — no logic to cover.
- **`figures.py` at 100% coverage is an execution claim, not a correctness
  claim.** V6 above is the open half of this; the limitation being recorded is
  that a line-coverage number will never speak to figure content.

---

## Verification

The gates for this package, in the order to run them. All four were green in this
tree on 2026-08-05, after the C1 fix.

```bash
cd "$(git rev-parse --show-toplevel)"                   # this package's repository root
uv sync --extra dev                                    # wires the bond-api path dependency; required before pytest

uv run pytest tests/ --cov=src --cov-fail-under=90     # expect: 234 passed, 100.00% coverage, 0 skips
uv run ruff check src/ scripts/                        # expect: All checks passed!
uv run ruff format --check src/ scripts/               # expect: 26 files already formatted
uv run mypy src/ scripts/                              # expect: Success: no issues found in 20 source files
```

Then confirm the tree regenerates and the lineage is clean:

```bash
uv run python scripts/generate_figures.py                   # 8 PNGs under output/figures/
uv run python scripts/z_generate_manuscript_variables.py    # strict: an unresolved {{TOKEN}} fails the run
rg -n "template[_]code_project" .                           # expect: zero hits
git status                                                  # expect: clean after committing (output/ is ignored)
```

And that hydration is byte-identical — the two hashes must match (C1):

```bash
uv run python scripts/z_generate_manuscript_variables.py
find output -type f \( -name '*.json' -o -name '*.md' \) | sort | xargs cat | md5
sleep 2
uv run python scripts/z_generate_manuscript_variables.py
find output -type f \( -name '*.json' -o -name '*.md' \) | sort | xargs cat | md5
```

And end to end, twice — the two runs must print the same input hash:

```bash
uv run python scripts/run_mission.py
uv run python scripts/run_mission.py --json
```

Do not trust the counts quoted in this file; run the commands. `AGENTS.md` and
`domain_profile.yaml` hold the authoritative gate definitions.


---

## Round-2 (2026-08-06)

Round-2 improvement pass: turned the open correctness gap **C3** into a
complete enumerator, and closed the verification backlog **V1-V7**, **D1**,
**D2**, **C2**, and the cargo-sweep extension **E4** — each with regression or
negative-control test evidence (zero mocks).

### Findings fixed (test evidence)

- **C3 — money cycles now enumerate completely (Johnson 1975).**
  `casino_network.find_money_cycles` was a back-edge DFS that dropped a circuit
  re-entering an already-visited node, under-reporting `laundering_closure` on
  overlapping graphs (the TODO's own counterexample). It is replaced by a
  complete elementary-circuit enumeration (Johnson 1975, following Tarjan
  1973), verified against an independent brute-force reference. The canonical
  network is unchanged (3 circuits, closure 0.7742), so no published number
  moved. Tests:
  `tests/test_casino_network.py::test_a_circuit_reentering_a_shared_done_node_is_not_lost`
  (the C3 counterexample now finds both circuits) and
  `test_enumerator_is_complete_against_a_reference` (reported set == reference
  set, no duplicates, including the recursive-unblock arms). Manuscript
  `02_methodology.md` and `07_scope_and_related_work.md` now state complete
  enumeration; `johnson1975` added to `references.bib`.
- **C2 — `bond-api` path is relative.** `pyproject.toml`
  `[tool.uv.sources]` changed from an absolute machine path to
  `{ path = "../bond-api" }`. Verified by copying the whole bond tree to another
  path, `uv sync --extra dev`, and passing the suite there.
- **V1 — claim ledger self-binding.** `data/claim_ledger.yaml` sources
  rewritten as executable expressions; `tests/test_claims.py` asserts the exact
  21-id set and recomputes every row from its `source` (1% relative tolerance
  for rounded floats). A row added without a source, or a source that drifts,
  now fails.
- **V2 — beam slant range bound to geometry.** The beam scenario's 36,998.4 km
  is asserted equal to the geometry's Washington DC slant range
  (`test_round2_verification.py::test_beam_slant_range_binds_to_the_geometry_it_claims`).
- **V3 — package version single-sourced.** pyproject, `__init__.__version__`,
  `mission.PACKAGE_VERSION`, and the manuscript config version are asserted
  equal.
- **V4 — token gate closed both ways.** A generated-but-uncited token (orphan)
  now fails, alongside the existing unknown-token forward gate.
- **V5 — pure-core importability tested.** A subprocess installs a
  `sys.meta_path` blocker for `bond_api` and asserts the seven pure modules
  (plus manifest/figures) import while `mission` is the only failure.
- **V6 — figure content bound + byte-identity.** `figures.py` gains
  `benford_figure_data()` / `cargo_sweep_figure_data()`; tests assert the
  plotted series equal the authoritative core, and a byte-identity test proves
  all eight renders are reproducible.
- **V7 — ablation rows enforced.** Recomputed for lot forensics (widen density
  window -> only `excessive_loss`, verdict `suspicious`) and corridors (single
  chain -> reduction exactly 0).
- **D1 — Airy encircled-energy named.** The full-power-inside-first-null
  assumption (≈83.8% inside the first null, ≈1.19x optimistic irradiance,
  ≈4.6% small diameter) is now cited in `07_scope_and_related_work.md`'s
  Limitations and in the `beam_physics` module docstring.
- **D2 — `tests/PATTERNS.md` fixed.** `OrbitalsSatellite` ->
  `orbital_mirror.Satellite` (with import), plus the completeness and
  two-way-token patterns.
- **E4 — cargo-value sweep (as measured, honest).** Added
  `smuggling_routes.cargo_reduction_sweep` and `CargoSweepPoint`, the live
  8th figure `cargo_sweep.png` (bound in `03_results.md` / figure protocols),
  and `experiment_plan.yaml` / `domain_profile.yaml` updates. Sweeping revealed
  the TODO's proposed "monotone reduction" premise is **false** for this
  network: reduction is non-negative but dips then rises as the optimum
  switches from the Paris leg to the New York leg — the sweep is reported and
  tested as measured, with no monotone trend asserted.

### Gate numbers (re-measured 2026-08-06)

- `uv run pytest tests/ --cov=src --cov-fail-under=90` → **251 passed**,
  **100.00%** line+branch coverage, **0 skipped / 0 failed** (234 passed before
  round-2 additions).
- `uv run ruff check src/ scripts/` — clean; `uv run ruff format --check
  src/ scripts/` — 26 files formatted; `uv run mypy src/ scripts/` — no issues
  in 20 files.
- Determinism: two mission runs print the same input hash (`0a6e93ab…`);
  8 figures and 63 tokens hydrate; `template[_]code_project` lineage grep
  returns only the intentional doc self-references.

### Left for a future round

- **E1** (provenance-export CLI), **E2** (satellite strike scheduling), and
  **E3** (a second forensic channel, e.g. refractive index) remain open
  extensions — untouched this round, and still valid as written.
