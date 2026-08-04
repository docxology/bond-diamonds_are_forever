# Methodology

The CONFLICT STONE mission combines three deterministic methods, each a pure
function of a fixed canonical dataset.

## Provenance chain

A custody chain is an ordered sequence of handoffs, each carrying a source, a
target, and a `recorded` flag. A valid chain is **continuous** (each handoff's
target is the next handoff's source) and **acyclic** (a gem never returns to a
previous holder). A handoff flagged `recorded=False` is a **break point** —
evidence that provenance cannot be verified at that step. The analytic surface
reports the break-point indices, the documented-coverage ratio, and whether the
chain is conflict-free.

## Casino money movement

The Las Vegas network is a directed, weighted graph whose edges aggregate
inter-casino transfers. The analysis computes gross flow, net positions, the
network **hub** (greatest gross flow), the set of directed **money cycles**
(laundering loops, found by a deterministic depth-first search), and the
**laundering closure** — the fraction of total flow that sits on a cycle. A
closure near one signals that money visibly circulates rather than passing
straight through.

## Orbital-mirror targeting geometry

A geostationary mirror above a sub-satellite point is modelled as a point on
the target sphere. Targeting solves the geometry that governs a strike:

- **Occultation** — the beam ray's nearest approach to Earth's centre; if it
  dips below the surface, the target is behind the limb and cannot be struck.
- **Slant range** — the straight-line distance the beam must travel.
- **Elevation** — the mirror's angle above the target's local horizon.
- **Beam delivery** — captured solar power (mirror area times the solar
  constant) and the irradiance implied for a focused spot.

All geometry is plain vector math over the standard Earth radius and solar
constant; there is no randomness.
