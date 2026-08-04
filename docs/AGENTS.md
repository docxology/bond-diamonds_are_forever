# docs/ — AGENTS.md

Rules for editing documentation in this BOND film package.

- Keep every claim traceable to code: when a metric changes, update the
  relevant section in `manuscript/` **and** the token value flows from
  `src/diamonds_are_forever/manuscript_variables.py` — never restate a number.
- Preserve the layer contract in `architecture.md` (pure core must not import
  `bond_api` / `infrastructure`).
- Keep the testing conventions in `testing_philosophy.md` accurate (no mocks,
  coverage-gated).
- Do not reintroduce `template[_]code_project` lineage strings.
- Consult `agent_instructions.md` before making operational changes.
