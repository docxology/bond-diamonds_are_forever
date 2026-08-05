# Methodology

The CONFLICT STONE mission combines seven deterministic methods, each a pure
function of a fixed canonical dataset.

## Provenance chain

A custody chain is an ordered sequence of handoffs, each carrying a source, a
target, and a `recorded` flag. A valid chain is **continuous** (each handoff's
target is the next handoff's source) and **acyclic** (a gem never returns to a
previous holder). A handoff flagged `recorded=False` is a **break point** —
evidence that provenance cannot be verified at that step. The analytic surface
reports the break-point indices, the documented-coverage ratio, and whether the
chain is conflict-free.

## Smuggling corridor routing

The chain answers *who touched the goods*; corridor routing answers *which
route they travel*. A smuggler moves a fixed-value cargo through a directed
network of corridors, each carrying a transport cost and a seizure probability.
The expected cost of a corridor is `cost + p_seizure * cargo_value`. A
deterministic Dijkstra over expected cost returns the **least-risk route**, its
expected cost, and its survival (`product(1 - p)`). A fewest-hops BFS baseline
in the *same* graph bounds the **reduction** metric, which is therefore always
non-negative.

## Lot forensics

Physical laundering of a lot is audited handoff-by-handoff against three
forensic rules: a **weight gain** (impossible for a genuine lot) flags
accounting fraud or substitution; a **loss beyond the legitimate cutting
allowance** of {{LOT_CUTTING_ALLOWANCE_PCT}} per handoff flags theft; and a
**measured density outside the diamond window**
({{LOT_DENSITY_MIN}}-{{LOT_DENSITY_MAX}} g/cm3 around nominal
{{LOT_DENSITY_NOMINAL}}) flags a paste or simulant swap. Each violation
contributes to an audit score and a lot verdict
(`clean` / `suspicious` / `flagrant`); a single anomaly reads as *suspicious*,
two or more as *flagrant*.

## Casino money movement

The Las Vegas network is a directed, weighted graph whose edges aggregate
inter-casino transfers. The analysis computes gross flow, net positions, the
network **hub** (greatest gross flow — a degree-style centrality in the sense
of [@freeman1978]), the directed **money cycles** (laundering loops, enumerated
by a deterministic depth-first search over back edges, the classical circuit
problem of [@tarjan1973]), and the **laundering closure** — the fraction of
flow that sits on a cycle.

## Benford's-law ledger audit

A laundering operation breaks the leading-digit distribution of its ledger by
clustering deposits on round figures. This module compares the ledger's
observed leading digits against Benford's law, `p(d) = log10(1 + 1/d)`
[@benford1938; @newcomb1881], with a Pearson chi-square statistic
[@pearson1900] against the df={{BENFORD_DF}}, alpha={{BENFORD_ALPHA}} critical
value of {{BENFORD_CRITICAL_VALUE}}. Above the critical value the ledger is
flagged **anomalous** — the laundering signal that forensic digit analysis is
built to surface [@nigrini2012].

**The audit is exercised as a matched control pair.** A screen that fires on
every ledger detects nothing, so the canonical ledger is built from two halves
that are also audited separately:

- a **legitimate baseline** of {{BENFORD_LEGIT_TRANSACTIONS}} transactions —
  the *negative control*. Its leading digits are the leading digits of the
  Fibonacci sequence, which are Benford-distributed as a theorem: Binet's
  formula makes `log10 F_n` an irrational rotation, equidistributed mod 1 by
  Weyl's criterion. Conformance is therefore a property of the sequence, not
  of digit frequencies chosen to pass the test. The amounts are placed across
  the 10^2-10^4 decades, and scaling by a power of ten cannot change a leading
  digit;
- {{BENFORD_LAUNDERED_TRANSACTIONS}} **round-figure deposits** on
  1/2/5 x 10^n — the laundered cash.

Both halves are constructed fixtures, not empirical records. The pair
establishes that this implementation separates them; it is not evidence about
how the screen would behave on real books.

## Orbital targeting geometry

A geostationary mirror is modelled as a point above a sub-satellite point.
Targeting solves occultation (the beam ray's nearest approach to Earth's
centre), slant range, and elevation above the target's horizon.

## Beam delivery physics

The targeting geometry solves *where* the beam can go; beam physics solves
*what it delivers*. A diffraction-limited Airy spot `r = 1.22 * lambda * R / D`
[@airy1835; @bornwolf1999] sets the focused size, Beer-Lambert
`T = exp(-k * L)` [@beer1852] sets the atmospheric transmittance, the power
budget `P = S * (pi D^2 / 4) * T` sets the captured flux, and the dwell time
`t = F / I` deposits a material's vaporization fluence. Chaining these gives
`I = S * T * D^4 / (4 * 1.22^2 * lambda^2 * R^2)`; inverting it for `D` yields
the **minimum mirror diameter** that delivers a required irradiance at a given
range — the honest bound on the weapon's fantasy, and the reason the result
scales only as the fourth root of the demanded irradiance.
