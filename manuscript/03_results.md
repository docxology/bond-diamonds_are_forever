# Results

All results are computed at runtime from the frozen canonical datasets; the
prose below cites resolving variables rather than hand-authored numbers.

## Provenance chain

The canonical route tracks a diamond lot through {{PROVENANCE_TRANSFERS}}
handoffs from mine to fence. {{PROVENANCE_BREAKPOINTS}} of those handoffs are
undocumented — the smuggling hops that make the lot conflict goods — giving a
documented coverage of {{PROVENANCE_COVERAGE_PCT}}. The chain is therefore
conflict-free = **{{PROVENANCE_CONFLICT_FREE}}**. Figure
[@fig:provenance] marks each handoff as documented or a break point.

![Provenance chain: documented handoffs vs. break points](../output/figures/provenance_chain.png){#fig:provenance}

## Smuggling corridor routing

Across a {{SMUGGLE_CORRIDORS}}-corridor network at a
{{SMUGGLE_EXPECTED_COST_M}} M USD expected cost, the stochastic-optimum route
is **{{SMUGGLE_ROUTE}}**, carrying the cargo with survival
{{SMUGGLE_SURVIVAL_PCT}}. Compared to the fewest-hops baseline this cuts
expected cost by {{SMUGGLE_REDUCTION_PCT}}. Figure [@fig:smuggling] plots the
corridor expected costs with the optimum route marked.

![Smuggling corridor expected costs (red = optimum route)](../output/figures/smuggling_route.png){#fig:smuggling}

## Lot forensics

Auditing {{LOT_SAMPLES}} handoff samples of lot DF-71 by weight and density
surfaces **{{LOT_ANOMALIES}} anomalies** and a {{LOT_AUDIT_SCORE}}-point audit
score — a **{{LOT_VERDICT}}** verdict. The density probe catches the Amsterdam
paste substitution; the weight ledger catches the final theft. Figure
[@fig:lot] shows the per-handoff weight deltas against the cutting allowance.

![Lot DF-71 weight reconciliation](../output/figures/lot_forensics.png){#fig:lot}

## Casino money movement

The strip network resolves to {{CASINO_CASINOS}} casinos and
{{CASINO_TRANSFERS}} transfers moving {{CASINO_TOTAL_FLOW_M}} million US
dollars in aggregate. The network hub is the **{{CASINO_HUB}}** operation.
Detection surfaces {{CASINO_MONEY_CYCLES}} distinct money cycles, and the
laundering closure — the share of flow that circulates — is
{{CASINO_LAUNDERING_CLOSURE_PCT}}. Figure [@fig:casino] visualises the graph.

![Las Vegas casino money movement](../output/figures/casino_network.png){#fig:casino}

## Benford's-law ledger audit

The {{BENFORD_TRANSACTIONS}}-transaction casino ledger yields a chi-square
statistic of **{{BENFORD_CHI_SQUARE}}** against Benford's law — a verdict of
**{{BENFORD_VERDICT}}** at the 0.05 critical value. Figure [@fig:benford]
compares the observed leading-digit distribution with the Benford expectation.

![Casino ledger vs. Benford's law](../output/figures/benford_ledger.png){#fig:benford}

## Orbital-mirror targeting

At a geostationary post of {{ORBITAL_ALTITUDE_KM}} km, the mirror surveys
{{ORBITAL_TARGETS}} threatened cities, of which {{ORBITAL_VISIBLE_TARGETS}}
fall within the visible face: {{ORBITAL_VISIBLE_NAMES}}. The remaining target
is occulted by the Earth. Figure [@fig:orbital] reports the slant range of
each target, shaded by beam visibility.

![Orbital-mirror slant range and visibility](../output/figures/orbital_visibility.png){#fig:orbital}

## Beam delivery physics

At a {{BEAM_SPOT_RADIUS_M}}-m diffraction-limited spot, the canonical mirror
delivers a beam concentrated {{BEAM_CONCENTRATION_X}}× over sunlight and
would take {{BEAM_VAPORIZE_TIME_S}} seconds to vaporize a steel layer. The
physics sets an honest bound on the weapon's fantasy: delivering 1 MW/m$^2$ at
geostationary range requires a {{BEAM_MIN_MIRROR_DIAMETER_M}}-m mirror. Figure
[@fig:beam] shows delivered irradiance versus mirror diameter with the
requirement marked.

![Beam delivery vs. mirror size at GEO](../output/figures/beam_physics.png){#fig:beam}

## Mission outcome

The execute phase aggregates these seven lines into a single deterministic
outcome carrying a full provenance block (package version, seed, and a SHA-256
input fingerprint). The debrief distills the standing lessons: an undocumented
handoff is a provenance break; seizure risk rewrites the route; weight and
density tell the physical story; circular money movement and a failing
Benford test are the laundering signatures; and beam physics bounds the
orbital weapon.
