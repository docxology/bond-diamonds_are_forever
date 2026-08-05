# Introduction

**{{CONFLICT_TITLE}}** (**{{CONFLICT_SUBTITLE}}**) is the CONFLICT STONE mission
package of PROJECT BOND, a suite of deterministic special-agent mission
analyses. Each film package implements the frozen BOND-API mission protocol,
which fixes the contract every mission must satisfy: a `brief`, a `recon`, a
`plan`, an `execute`, and a `debrief`, each carrying typed provenance so an
outcome can be audited without re-running the mission.

This package's identity is `{{CONFLICT_IDENTITY}}`, version
{{CONFLICT_VERSION}}, under codename {{CONFLICT_CODENAME}}. It adapts seven
pure analytic cores to the protocol, tracing the film's operation from the mine
to the satellite:

1. **Provenance chain** — a conflict-diamond custody graph with documented
   handoffs and identified provenance break points.
2. **Smuggling routes** — a directed corridor network in which each leg carries
   a transport cost and a seizure probability; an expected-cost shortest path
   is compared against a fewest-hops baseline in the same graph.
3. **Lot forensics** — weight and density reconciliation of the physical lot
   across its handoffs, separating legitimate cutting loss from theft and from
   paste substitution.
4. **Casino network** — directed money movement across the Las Vegas strip,
   with cycle detection, laundering-closure measurement, and hub discovery.
5. **Benford audit** — a leading-digit test of the casino ledger against
   Benford's law, scored by a Pearson chi-square statistic.
6. **Orbital mirror** — geostationary space-mirror targeting geometry:
   occultation, slant range, and elevation above the target's horizon.
7. **Beam physics** — what the mirror actually delivers: the diffraction-limited
   spot, atmospheric transmittance, the power budget, and the minimum mirror
   diameter a strike-class beam would require.

The first five cores prosecute the terrestrial half of the operation (who
touched the stones, how they moved, whether they are genuine, and where the
money went); the last two bound the orbital half in physics rather than in
plot. The mission software is a thin adapter over these cores: the domains are
pure and infrastructure-free, while the adapter handles only the protocol
wiring. This keeps every analytic claim testable in isolation and reproducible
by construction.
