# Experimental Setup

All experiments are deterministic and use fixed canonical datasets seeded into
the pure domain core; there is no random number generation and no mock
framework.

**Mission configuration.** The package identity `{{CONFLICT_IDENTITY}}` runs
under codename `{{CONFLICT_CODENAME}}`, version {{CONFLICT_VERSION}}. Keywords
of the analysis: {{CONFLICT_KEYWORDS}}.

**Provenance dataset.** {{PROVENANCE_TRANSFERS}} ordered custody handoffs along
the mine-to-fence route. Break points are flagged at build time; the coverage
ratio is derived from them.

**Casino dataset.** {{CASINO_CASINOS}} casinos with {{CASINO_TRANSFERS}}
transfers totalling {{CASINO_TOTAL_FLOW_M}} million US dollars. Amounts are
exact float values accumulated in insertion order.

**Orbital dataset.** {{ORBITAL_TARGETS}} ground targets surveyed from a
geostationary post at {{ORBITAL_ALTITUDE_KM}} km. Geometry uses the standard
Earth radius and solar constant; no ephemeris is simulated.

**Software environment.** Python {{PYTHON_VERSION}}, resolved at generation
time. Variable generation timestamp: {{GENERATION_TIMESTAMP}} (UTC).
