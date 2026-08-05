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
| `test_benford_audit.py` | leading-digit law, chi-square, report verdict, the negative-control/positive-case pair, validation errors |
| `test_orbital_mirror.py` | occultation, slant range, elevation, beam power, validation errors |
| `test_beam_physics.py` | diffraction spot, Beer-Lambert, vaporization, min-mirror inversion |
| `test_mission.py` | MissionProvider lifecycle, protocol check, discovery, gadgets, serialization |
| `test_manuscript_variables.py` | token map, constant-derivation bindings, live `{{TOKEN}}` cross-reference gate |
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
- **Constant-derivation bindings**:
  `test_model_constant_tokens_track_the_core_constants` asserts each token that
  stands in for a model constant is *derived* from that constant. Without it, a
  token could be hand-set to a plausible string and the manuscript would drift
  silently — the exact failure the token system exists to prevent.
- **Subprocess smoke** runs scripts with `sys.executable`, `cwd=<package root>`,
  asserting exit code 0 and expected stdout/artifact presence.

## Tests that stand in for removed guards

Where a guard was structurally unable to fail, it was deleted and replaced by a
test asserting the invariant. A dead branch is worse than no branch: it reads
as safety, contributes nothing, and hides the fact that the property was never
checked. Three cases:

| Removed | Replacement test |
|---|---|
| A `digit == 10` clamp in `first_digit` (the scaling loops exit only on `1.0 <= m < 10.0`) | `test_first_digit_is_exact_across_the_whole_magnitude_range` sweeps the double exponent range against an independent `Decimal` oracle |
| A cycle de-duplication filter in `find_money_cycles` (edges are unique by construction, so each back edge yields one cycle) | `test_reported_cycles_are_distinct_without_a_dedup_pass` asserts distinctness on a dense graph |
| A fourth `elif` on a three-valued anomaly code | the `else` arm plus the existing per-rule scoring tests |

## Negative controls

A detector that fires on every input has not been shown to detect anything, so
a positive result is only readable next to a negative control that the same
code path passes.

The Benford audit is the case in point. It originally shipped with only a
positive result: the canonical ledger scored 44.06 and was flagged anomalous.
But the ledger's supposedly legitimate half — 40 amounts confined to one
decade and near-uniform across leading digits (4,4,4,5,4,5,5,5,4) — scored
19.38 on its own, above the 15.507 critical value. A ledger containing *only*
the clean transactions would have been flagged too, and roughly 8 points of
the headline 44.06 came from the baseline rather than from any laundering. The
demonstration could not distinguish "the audit detects structuring" from "the
audit rejects everything".

The fix was to make the baseline genuinely conforming for a reason external to
the test: its leading digits are now the leading digits of the Fibonacci
sequence, which are Benford-distributed by theorem (`log10 F_n` is an
irrational rotation, equidistributed mod 1). Nothing was tuned against the
chi-square statistic, and
`test_legitimate_baseline_leading_digits_are_the_fibonacci_digits` recomputes
the sequence independently and checks the amounts digit-for-digit, so the
provenance cannot be quietly swapped for hand-picked frequencies.

Three assertions now carry the claim:
`test_legitimate_baseline_conforms_the_negative_control` (clean half passes),
`test_laundered_deposits_alone_are_anomalous` (dirty half fails), and
`test_audit_discriminates_the_two_halves` (the verdict flips on exactly the
addition of the deposits). Each was confirmed falsifiable by restoring the old
baseline — the control test goes red with `conforms=False, chi_square=19.3761`
— and by setting the critical value to 0.1, which also turns it red. Both are
required: the first proves the control binds the *data*, the second that it
binds the *detector*.

What this establishes is specificity on two constructed fixtures. It is not a
false-positive rate, and the manuscript says so.

## Oracle discipline

An oracle must be a *different mechanism* from the code it checks, or the test
is a restatement. `first_digit` is verified against `Decimal(float)` — exact
but structurally unrelated to the integer-ratio scaling in the implementation.
Two oracles were rejected during this work for being wrong rather than merely
weak: `%e` formatting rounds (Benford is defined on truncation), and the
implementation's own algorithm would have been circular.

Sweeps also assert their own coverage — `assert checked > 3000` — so a sweep
whose loop silently stops matching cannot pass by examining nothing.
