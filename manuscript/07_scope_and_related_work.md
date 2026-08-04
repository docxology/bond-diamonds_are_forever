# Scope and Related Work

## Scope

This package analyses the three traces central to *Diamonds Are Forever*:
conflict-diamond provenance, casino money movement, and orbital-mirror
targeting. It is **self-contained and illustrative**: the canonical datasets
are fixed, small, and embedded in the pure core. It is not a claim about any
real investigation, casino, or satellite system; it is a deterministic,
reproducible demo of the analytic methods, in the tradition of special-agent
mission models.

## Related work

- The conflict-diamond provenance model generalises the supply-chain
  certification approach documented by the Kimberley Process
  [@kimberley2003], which formalises the "documented handoff" as the unit of
  verifiable traceability. The break-point analysis echoes the failure-mode
  reporting of early conflict-goods investigations [@globalwitness1998].
- The laundering-closure measure is a deterministic, closure-based variant of
  circular money-movement detection in financial network analysis: a cycle in
  a directed weighted graph is the structural signature of value returning to
  its origin.
- The orbital targeting is a simple line-of-sight / slant-range geometry; it
  deliberately omits orbital mechanics, atmospherics, and beam physics, which
  are out of scope for this mission package. The contrast sets the boundary:
  this work's contribution is reproducible, deterministic analysis, not a
  flight-dynamics claim.

The package also documents its own platform: CONFLICT STONE ({{CONFLICT_TITLE}})
is one member of the PROJECT BOND suite, which shares the frozen BOND-API
mission protocol [@bondapi2026].
