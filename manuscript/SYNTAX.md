# Manuscript Syntax — diamonds_are_forever (CONFLICT STONE)

Project-specific overlay for the manuscript rendering syntax. The relevant
canonical guide lives in the shared template docs; this file records the
**diamonds_are_forever**-specific token and figure protocol.

## {{TOKEN}} protocol

Every numeric/metric token in a numbered section resolves through
`src/diamonds_are_forever/manuscript_variables.py::generate_variables()`,
which reads `manuscript/config.yaml` plus the pure analytic core. Never
hand-author a metric in prose.

Full token list (source of truth: `generate_variables()` return dict):

```
CONFLICT_IDENTITY, CONFLICT_CODENAME, CONFLICT_TITLE, CONFLICT_SUBTITLE,
CONFLICT_VERSION, CONFLICT_KEYWORDS,
PROVENANCE_TRANSFERS, PROVENANCE_BREAKPOINTS, PROVENANCE_COVERAGE_PCT,
PROVENANCE_CONFLICT_FREE,
CASINO_CASINOS, CASINO_TRANSFERS, CASINO_TOTAL_FLOW_M, CASINO_HUB,
CASINO_MONEY_CYCLES, CASINO_LAUNDERING_CLOSURE_PCT,
ORBITAL_ALTITUDE_KM, ORBITAL_TARGETS, ORBITAL_VISIBLE_TARGETS,
ORBITAL_VISIBLE_NAMES,
PYTHON_VERSION, GENERATION_TIMESTAMP
```

To add a token: add the key in `generate_variables()`, wire it into the
relevant numbered section, and regenerate. The live cross-reference gate in
`tests/test_manuscript_variables.py` fails if a section uses an unknown token.

Note: this guide intentionally shows literal brace forms for illustration;
the numbered sections must not.

## Figures

| Label | PNG (relative) | Generator |
|---|---|---|
| `{#fig:provenance}` | `../output/figures/provenance_chain.png` | `figures.generate_provenance_figure` |
| `{#fig:casino}` | `../output/figures/casino_network.png` | `figures.generate_casino_figure` |
| `{#fig:orbital}` | `../output/figures/orbital_visibility.png` | `figures.generate_orbital_figure` |

Reference figures via Pandoc-crossref: `[@fig:provenance]` or `@fig:casino`;
never a hardcoded number. Regenerate figures with
`uv run python scripts/generate_figures.py`.
