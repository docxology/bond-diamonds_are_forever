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
  space as the naive baseline.
- The money-movement analysis draws on the laundering-detection literature
  [@levi2006]. Cycle detection is the elementary-circuit enumeration problem
  [@tarjan1973] restricted to the small canonical graph, and the hub is a
  gross-flow reading of degree centrality [@freeman1978].
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
