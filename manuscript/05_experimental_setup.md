# Experimental Setup

All experiments are deterministic and use fixed canonical datasets seeded into
the pure domain core; there is no random number generation and no mock
framework.

**Mission configuration.** The package identity `{{CONFLICT_IDENTITY}}` runs
under codename `{{CONFLICT_CODENAME}}`, version {{CONFLICT_VERSION}}. Keywords
of the analysis: {{CONFLICT_KEYWORDS}}.

**Provenance dataset.** {{PROVENANCE_TRANSFERS}} ordered custody handoffs along
the mine-to-fence route; break points are flagged at build time.

**Smuggling dataset.** A {{SMUGGLE_CORRIDORS}}-corridor directed network of
transport costs and seizure probabilities, given a cargo value of
${{SMUGGLE_EXPECTED_COST_M}} million US dollars. The least-risk route is computed
by a deterministic Dijkstra; the baseline is a fewest-hops BFS in the same
network.

**Forensic dataset.** {{LOT_SAMPLES}} weight/density handoff samples for lot
DF-71, audited against a {{LOT_AUDIT_SCORE}} score.

**Casino dataset.** {{CASINO_CASINOS}} casinos with {{CASINO_TRANSFERS}}
transfers totalling {{CASINO_TOTAL_FLOW_M}} million US dollars, and a
{{BENFORD_TRANSACTIONS}}-transaction ledger for the digit-law test.

**Orbital dataset.** {{ORBITAL_TARGETS}} ground targets surveyed from a
geostationary post at {{ORBITAL_ALTITUDE_KM}} km, plus the beam-physics
scenario (mirror size, wavelength, slant range, atmospheric attenuation).

**Software environment.** Python {{PYTHON_VERSION}}, resolved at generation
time. Variable generation timestamp: {{GENERATION_TIMESTAMP}} (UTC).
