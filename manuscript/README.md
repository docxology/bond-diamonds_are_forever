# manuscript/ — diamonds_are_forever (CONFLICT STONE)

Source for the CONFLICT STONE manuscript. Numbered `NN_*.md` sections are the
rendering input; `config.yaml` drives the `{{TOKEN}}` values.

- Hydrate every `{{TOKEN}}` with `scripts/z_generate_manuscript_variables.py`
  (strict by default).
- See `AGENTS.md` for the token + figure protocol and the cross-reference gate.
- Metrics flow from `../src/diamonds_are_forever/manuscript_variables.py` —
  never restate a number in prose.
