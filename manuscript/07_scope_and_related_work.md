# Scope and Related Work

## Scope

This package analyses the traces central to *Diamonds Are Forever*:
conflict-diamond provenance and corridor routing, physical lot forensics,
casino money movement and its Benford signature, and the orbital mirror's
targeting geometry and beam physics. It is **self-contained and illustrative**:
the canonical datasets are fixed, small, and embedded in the pure core. It is
not a claim about any real investigation, casino, or satellite system; it is a
deterministic, reproducible demo of the analytic methods, in the tradition of
special-agent mission models.

## Related work

- The provenance and forensic models generalise real supply-chain certification
  and diamond identification practice: the Kimberley Process formalises the
  "documented handoff" as the unit of traceability [@kimberley2003], early
  conflict-goods investigations documented the route and its gaps
  [@globalwitness1998], and the economics of mineral-driven conflict are
  quantified in [@berman2017]. Diamond density testing follows standard
  gemological identification [@webster1994].
- The corridor routing is a textbook shortest-path problem over expected cost;
  Dijkstra's algorithm [@dijkstra1959] bounds optimality over the same search
  space as the naive baseline. The cargo-value sensitivity is swept as data
  because the optimum is cargo-dependent (cheap corridors at low value,
  low-seizure corridors at high value), not monotone.
- The money-movement analysis draws on the laundering-detection literature
  [@levi2006]. Cycle detection is a *complete* elementary-circuit enumeration
  [@tarjan1973; @johnson1975] restricted to the small canonical graph, and the
  hub is a gross-flow reading of degree centrality [@freeman1978].
- The ledger audit rests on the leading-digit law observed by Newcomb
  [@newcomb1881] and rediscovered by Benford [@benford1938], scored with
  Pearson's chi-square criterion [@pearson1900]; its use as a fraud indicator
  follows forensic-accounting practice [@nigrini2012]. The test is a screen,
  not a proof: a failing ledger warrants investigation, it does not by itself
  establish laundering.
- The beam physics uses the Airy diffraction pattern [@airy1835] and the
  exponential absorption law [@beer1852], both as given in classical optics
  [@bornwolf1999]. It deliberately omits orbital mechanics, beam-riding
  control, adaptive optics, thermal blooming, and target material science
  beyond a single vaporization fluence, which are out of scope; the minimum
  mirror diameter is therefore a lower bound on the real requirement, not an
  estimate of it.

The package also documents its own platform: CONFLICT STONE ({{CONFLICT_TITLE}})
is one member of the PROJECT BOND suite, which shares the frozen BOND-API
mission protocol [@bondapi2026].

## Limitations and uncertainty

These are the honest bounds on what the package establishes, recorded so they
are not over-read:

- **Constructed fixtures, not empirical records.** The Benford result is a
  specificity check on two designed halves of one ledger — a Fibonacci-derived
  negative control and round-figure deposits — so it establishes that this
  implementation separates *these two halves*, not a false-positive or
  false-negative rate. No detection accuracy is claimed or measured.
  Equally, the canonical custody chain, casino network, and orbital targets
  are illustrative by design (see *Scope*); they are chosen so each headline
  metric is non-trivial rather than vacuous, not to sample any real corpus.
- **The substitution finding rests on a single instrument.** Lot forensics
  separates paste from diamond on density alone (a second gemological channel
  such as refractive index is a stated extension, not implemented), so the
  density verdict is one-instrument. The weight-vs-density finding is
  nonetheless two-signal because theft (weight) and substitution (density) are
  audited independently.
- **The beam model bounds the weapon in one direction only.** It omits orbital
  mechanics, beam-riding control, adaptive optics, thermal blooming, and
  material science beyond one vaporization fluence. It also assumes the *full*
  captured power lands inside the first-null disk; the real Airy pattern puts
  ≈83.8% of the power inside the first null, making the delivered irradiance
  ≈1.19× optimistic and the minimum diameter ≈4.6% small. Every omission —
  this one included — pushes toward a *larger* honest mirror, which is why the
  result is presented as a lower bound on the requirement, never as an
  estimate.
- **Determinism is not evidence of correctness.** The outputs are exact and
  reproducible by construction, but a deterministic, passing pipeline is only
  as good as the model that produced it; the same is true of the 100% line
  coverage figure, which measures execution, not truth. Where the model's shape
  is wrong, reproducing it faithfully only reproduces the error.
- **Cargo-value behaviour is reported as measured.** The `route_reduction`
  sweep is *not* monotone in cargo value (it falls and then rises as the
  optimum switches corridors); no monotone trend is claimed, and the sweep
  figure plots the measured curve with the canonical value marked.