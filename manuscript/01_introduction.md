# Introduction

**{{CONFLICT_TITLE}}** (**{{CONFLICT_SUBTITLE}}**) is the CONFLICT STONE mission
package of PROJECT BOND, a suite of deterministic special-agent mission
analyses. Each film package implements the frozen BOND-API mission protocol,
which fixes the contract every mission must satisfy: a `brief`, a `recon`, a
`plan`, an `execute`, and a `debrief`, each carrying typed provenance so an
outcome can be audited without re-running the mission.

This package's identity is `{{CONFLICT_IDENTITY}}`, version
{{CONFLICT_VERSION}}, under codename {{CONFLICT_CODENAME}}. It adapts three
pure analytic cores to the protocol:

1. **Provenance chain** — a conflict-diamond custody graph with documented
   handoffs and identified provenance break points.
2. **Casino network** — directed money movement across the Las Vegas strip,
   with laundering-closure measurement and hub discovery.
3. **Orbital mirror** — geostationary space-mirror targeting geometry:
   line-of-sight, slant range, and beam delivery.

The mission software is a thin adapter over these cores: the domains are pure
and infrastructure-free, while the adapter handles only the protocol wiring.
This keeps every analytic claim testable in isolation and reproducible by
construction.
