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

## Casino money movement

The strip network resolves to {{CASINO_CASINOS}} casinos and
{{CASINO_TRANSFERS}} transfers moving {{CASINO_TOTAL_FLOW_M}} million US
dollars in aggregate. The network hub is the **{{CASINO_HUB}}** operation.
Detection surfaces {{CASINO_MONEY_CYCLES}} distinct money cycles, and the
laundering closure — the share of flow that circulates — is
{{CASINO_LAUNDERING_CLOSURE_PCT}}. Figure [@fig:casino] visualises the graph.

![Las Vegas casino money movement](../output/figures/casino_network.png){#fig:casino}

## Orbital-mirror targeting

At a geostationary post of {{ORBITAL_ALTITUDE_KM}} km, the mirror surveys
{{ORBITAL_TARGETS}} threatened cities, of which {{ORBITAL_VISIBLE_TARGETS}}
fall within the visible face: {{ORBITAL_VISIBLE_NAMES}}. The remaining target
is occulted by the Earth — the geometric bound that caps any such weapon's
coverage. Figure [@fig:orbital] reports the slant range of each target,
shaded by beam visibility.

![Orbital-mirror slant range and visibility](../output/figures/orbital_visibility.png){#fig:orbital}

## Mission outcome

The execute phase aggregates these three lines into a single deterministic
outcome carrying a full provenance block (package version, seed, and a
SHA-256 input fingerprint). The debrief distills the standing lessons: an
undocumented handoff is a provenance break; circular money movement is the
laundering signature; an orbital mirror only strikes the visible face.
