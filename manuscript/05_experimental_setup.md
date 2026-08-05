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
transport costs and seizure probabilities, carrying a cargo valued at
{{SMUGGLE_CARGO_VALUE_M}} million US dollars. The least-risk route is computed
by a deterministic Dijkstra over expected cost; the baseline is a fewest-hops
BFS in the same network, which bounds the reduction metric below at zero.

**Forensic dataset.** {{LOT_SAMPLES}} weight/density handoff samples for lot
{{LOT_ID}}, audited against a {{LOT_CUTTING_ALLOWANCE_PCT}} per-handoff cutting
allowance and a {{LOT_DENSITY_MIN}}-{{LOT_DENSITY_MAX}} g/cm3 density window
(nominal {{LOT_DENSITY_NOMINAL}}), yielding a {{LOT_AUDIT_SCORE}}-point score.

**Casino dataset.** {{CASINO_CASINOS}} casinos with {{CASINO_TRANSFERS}}
transfers totalling {{CASINO_TOTAL_FLOW_M}} million US dollars, and a
{{BENFORD_TRANSACTIONS}}-transaction ledger tested at df={{BENFORD_DF}},
alpha={{BENFORD_ALPHA}} (critical value {{BENFORD_CRITICAL_VALUE}}). The
ledger is a matched pair: a {{BENFORD_LEGIT_TRANSACTIONS}}-transaction
legitimate baseline drawn from Fibonacci leading digits (Benford-conforming by
theorem — the negative control) plus {{BENFORD_LAUNDERED_TRANSACTIONS}}
round-figure deposits. Each half is audited on its own as well as together.

**Orbital dataset.** {{ORBITAL_TARGETS}} ground targets surveyed from a
geostationary post at {{ORBITAL_ALTITUDE_KM}} km.

**Beam scenario.** A {{BEAM_MIRROR_DIAMETER_M}} m mirror at
{{BEAM_WAVELENGTH_NM}} nm over a {{BEAM_SLANT_RANGE_KM}} km slant range, with
atmospheric attenuation giving a transmittance of
{{BEAM_TRANSMITTANCE_PCT}}; the strike requirement against which the minimum
mirror is solved is {{BEAM_REQUIRED_IRRADIANCE_MW}} MW/m2.

**Software environment.** Python {{PYTHON_VERSION}}, resolved at generation
time. Variable generation timestamp: {{GENERATION_TIMESTAMP}} (UTC).
