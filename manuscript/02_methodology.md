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
allowance** flags theft; and a **measured density outside the diamond window**
(3.40-3.65 g/cm3 around nominal 3.52) flags a paste or simulant swap. Each
violation contributes to an audit score and a lot verdict
(`clean` / `suspicious` / `flagrant`).

## Casino money movement

The Las Vegas network is a directed, weighted graph whose edges aggregate
inter-casino transfers. The analysis computes gross flow, net positions, the
network **hub** (greatest gross flow), the directed **money cycles**
(laundering loops, via deterministic depth-first search), and the
**laundering closure** — the fraction of flow that sits on a cycle.

## Benford's-law ledger audit

A laundering operation breaks the natural leading-digit distribution of its
ledger (deposits cluster on round figures; the "legitimate" amounts rarely span
a natural magnitude). This module compares the ledger's observed leading
digits against Benford's law, `p(d) = log10(1 + 1/d)`, with a Pearson
chi-square statistic against the df=8, alpha=0.05 critical value. Above the
critical value the ledger is flagged **anomalous** — the laundering signal.

## Orbital targeting geometry

A geostationary mirror is modelled as a point above a sub-satellite point.
Targeting solves occultation (the beam ray's nearest approach to Earth's
centre), slant range, and elevation above the target's horizon.

## Beam delivery physics

The targeting geometry solves *where* the beam can go; beam physics solves
*what it delivers*. A diffraction-limited Airy spot `r = 1.22 * lambda * R / D`
sets the focused size, Beer-Lambert `T = exp(-k * L)` sets the atmospheric
transmittance, the power budget `P = S * (pi D^2 / 4) * T` sets the captured
flux, and the dwell time `t = F / I` deposits a material's vaporization
fluence. Inverting the chain yields the **minimum mirror diameter** that
delivers a required irradiance at a given range — the honest bound on the
weapon's fantasy.
