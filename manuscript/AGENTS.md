# Manuscript — diamonds_are_forever (CONFLICT STONE)

Repository-wide agent rules live in `../docs/agent_instructions.md`. This file
covers manuscript-specific editing: file roles, the `{{TOKEN}}` protocol, the
figure protocol, and the token cross-reference gate.

## File inventory

| File / Pattern | Role |
|---|---|
| `00_abstract.md` | Abstract; summary tokens for all seven analytic lines |
| `01_introduction.md` | Platform intro, protocol, package identity |
| `02_methodology.md` | The seven analytic methods |
| `03_results.md` | All results + all figures + result tokens |
| `04_conclusion.md` | Synthesis and guarantees |
| `05_experimental_setup.md` | Datasets, config, environment tokens |
| `06_reproducibility.md` | Determinism, provenance, recomputation |
| `07_scope_and_related_work.md` | Scope boundary + references |
| `99_references.md` | Bibliography |
| `config.yaml` | Paper/mission metadata; source of config tokens |
| `config.yaml.example` | Copy-and-customize template |
| `references.bib` | BibTeX bibliography |
| `preamble.md` | LaTeX injections |
| `layer_contract.yaml` | Module layer contract |
| `SYNTAX.md` | Token + figure protocol reference |

## {{TOKEN}} protocol

Numeric/metric values always use `{{TOKEN}}` syntax; they resolve through
`../src/diamonds_are_forever/manuscript_variables.py::generate_variables()`
from `config.yaml` + the pure analytic core. Never hardcode a metric in prose.

Pipeline: `scripts/z_generate_manuscript_variables.py` computes the map, writes
`output/data/manuscript_variables.json`, and hydrates numbered sections into
`output/manuscript/` (strict mode fails on unresolved tokens).

**Adding a token**: add the key in `generate_variables()`, use it in a numbered
section, then regenerate. The live cross-reference gate in
`../tests/test_manuscript_variables.py` asserts every `{{TOKEN}}` used in
`[0-9]*.md` resolves — it fails automatically if a manuscript token is missing.

**Detecting unresolved tokens**:

```bash
uv run python scripts/z_generate_manuscript_variables.py  # strict: fails on leftovers
```

## Figure protocol

Reference figures via Pandoc-crossref (`[@fig:label]`), never hardcoded
numbers or `\ref{}` directly:

| Label | PNG (relative) |
|---|---|
| `{#fig:provenance}` | `../output/figures/provenance_chain.png` |
| `{#fig:smuggling}` | `../output/figures/smuggling_route.png` |
| `{#fig:lot}` | `../output/figures/lot_forensics.png` |
| `{#fig:casino}` | `../output/figures/casino_network.png` |
| `{#fig:benford}` | `../output/figures/benford_ledger.png` |
| `{#fig:orbital}` | `../output/figures/orbital_visibility.png` |
| `{#fig:cargo}` | `../output/figures/cargo_sweep.png` |
| `{#fig:beam}` | `../output/figures/beam_physics.png` |

Regenerate with `scripts/generate_figures.py`; generator code lives in
`../src/diamonds_are_forever/figures.py`.

## Note on literal braces

This file and `SYNTAX.md` intentionally illustrate `{{TOKEN}}` syntax with
literal braces; the numbered `NN_*.md` sections must not contain raw braces. The
cross-reference gate scans only numbered sections.
