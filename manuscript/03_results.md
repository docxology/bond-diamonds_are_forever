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

Across a {{SMUGGLE_CORRIDORS}}-corridor network moving a
{{SMUGGLE_CARGO_VALUE_M}} M USD cargo, the stochastic-optimum route is
**{{SMUGGLE_ROUTE}}** at an expected cost of {{SMUGGLE_EXPECTED_COST_M}} M USD,
carrying the cargo with survival {{SMUGGLE_SURVIVAL_PCT}} (seizure exposure
{{SMUGGLE_EXPOSURE_PCT}}). The fewest-hops baseline in the same graph
({{SMUGGLE_NAIVE_ROUTE}}) costs {{SMUGGLE_NAIVE_COST_M}} M USD, so optimising
over expected cost rather than hop count cuts expected cost by
{{SMUGGLE_REDUCTION_PCT}}: at the same hop count, the optimum swaps the pricey
London-Amsterdam Channel ferry for the cheaper Paris leg. The two routes carry
almost the same seizure exposure — the saving is on transport cost, not on
seizure risk, which is why the survival probabilities barely differ. Figure
[@fig:smuggling] plots the corridor expected costs with the optimum route
marked.

![Smuggling corridor expected costs (red = optimum route)](../output/figures/smuggling_route.png){#fig:smuggling}

## Lot forensics

Auditing {{LOT_SAMPLES}} handoff samples of lot {{LOT_ID}} by weight and
density surfaces **{{LOT_ANOMALIES}} anomalies** and a
{{LOT_AUDIT_SCORE}}-point audit score — a **{{LOT_VERDICT}}** verdict. The
density probe catches the Amsterdam paste substitution (a measured density
outside the {{LOT_DENSITY_MIN}}-{{LOT_DENSITY_MAX}} g/cm3 window); the weight
ledger catches the final theft, a loss well beyond the
{{LOT_CUTTING_ALLOWANCE_PCT}} cutting allowance. The two rules are
independent — one physical, one accounting — so the verdict does not rest on a
single instrument. Figure [@fig:lot] shows the per-handoff weight deltas
against the cutting allowance.

![Lot weight reconciliation](../output/figures/lot_forensics.png){#fig:lot}

## Casino money movement

The strip network resolves to {{CASINO_CASINOS}} casinos and
{{CASINO_TRANSFERS}} transfers moving {{CASINO_TOTAL_FLOW_M}} million US
dollars in aggregate. The network hub is the **{{CASINO_HUB}}** operation.
Detection surfaces {{CASINO_MONEY_CYCLES}} distinct money cycles, and the
laundering closure — the share of flow that circulates — is
{{CASINO_LAUNDERING_CLOSURE_PCT}}. Figure [@fig:casino] visualises the graph.

![Las Vegas casino money movement](../output/figures/casino_network.png){#fig:casino}

## Benford's-law ledger audit

The audit is reported as a matched pair, so that the anomalous verdict can be
attributed to something.

**Negative control.** The legitimate baseline alone —
{{BENFORD_LEGIT_TRANSACTIONS}} transactions whose leading digits are the
Fibonacci leading digits, Benford-distributed by theorem rather than by
construction against the test — scores a chi-square of
**{{BENFORD_LEGIT_CHI_SQUARE}}**, far below the {{BENFORD_CRITICAL_VALUE}}
critical value: a verdict of **{{BENFORD_LEGIT_VERDICT}}**. The screen does not
fire on clean books.

**Full ledger.** Adding the {{BENFORD_LAUNDERED_TRANSACTIONS}} round-figure
deposits takes the same statistic, computed by the same code path, to
**{{BENFORD_CHI_SQUARE}}** over {{BENFORD_TRANSACTIONS}} transactions — above
the df={{BENFORD_DF}}, alpha={{BENFORD_ALPHA}} critical value of
{{BENFORD_CRITICAL_VALUE}}, a verdict of **{{BENFORD_VERDICT}}**. Because the
baseline passes on its own, the flag is attributable to the deposits and not
to the baseline.

Figure [@fig:benford] plots all three distributions — baseline, full ledger,
Benford expectation — so the separation is visible. Digit {{BENFORD_CARRIER_DIGIT}}
alone carries {{BENFORD_CARRIER_SHARE_PCT}} of the statistic — the 5 x 10^n
structuring. The full ledger runs above the Benford expectation on exactly the
digits the deposits sit on (1, 2 and 5) and below it on every other digit.

This is a specificity check on two constructed fixtures, not a measurement of
detection accuracy: it shows the implemented test separates *these* halves. No
false-positive or false-negative rate is estimated here, and none should be
read off it.

![Casino ledger vs. Benford's law: legitimate baseline (negative control), full ledger, and the Benford expectation](../output/figures/benford_ledger.png){#fig:benford}

## Orbital-mirror targeting

At a geostationary post of {{ORBITAL_ALTITUDE_KM}} km, the mirror surveys
{{ORBITAL_TARGETS}} threatened cities, of which {{ORBITAL_VISIBLE_TARGETS}}
fall within the visible face: {{ORBITAL_VISIBLE_NAMES}}. The remaining target
({{ORBITAL_OCCULTED_NAMES}}) is occulted by the Earth — no pointing solution
exists for it from this post, whatever the mirror's power. Figure
[@fig:orbital] reports the slant range of each target, shaded by beam
visibility.

![Orbital-mirror slant range and visibility](../output/figures/orbital_visibility.png){#fig:orbital}

## Beam delivery physics

The canonical scenario is a {{BEAM_MIRROR_DIAMETER_M}}-m mirror working at
{{BEAM_WAVELENGTH_NM}} nm over a {{BEAM_SLANT_RANGE_KM}} km slant range, with
an atmospheric transmittance of {{BEAM_TRANSMITTANCE_PCT}}. At the resulting
{{BEAM_SPOT_RADIUS_M}}-m diffraction-limited spot it delivers
{{BEAM_IRRADIANCE_W_M2}} W/m$^2$ — a beam concentrated
{{BEAM_CONCENTRATION_X}}× over raw sunlight, which would still need
{{BEAM_VAPORIZE_TIME_S}} seconds of dwell to vaporize a steel layer. The
physics sets an honest bound on the weapon's fantasy: delivering
{{BEAM_REQUIRED_IRRADIANCE_MW}} MW/m$^2$ at geostationary range requires a
{{BEAM_MIN_MIRROR_DIAMETER_M}}-m mirror. Because irradiance grows as the fourth
power of the diameter, that bound moves slowly — the mirror is the binding
constraint, and the dwell time is what a moving target denies. Figure
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
