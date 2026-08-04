# docs/ — diamonds_are_forever (CONFLICT STONE)

Agent- and human-facing documentation for the BOND film package.

| File | Purpose |
|---|---|
| `AGENTS.md` | Directory-level agent rules |
| `README.md` | This index |
| `agent_instructions.md` | Operational constraints and guardrails |
| `architecture.md` | Module boundaries, data flow, determinism |
| `testing_philosophy.md` | Mock-free, coverage-gated test conventions |

The authoritative source for every metric is the pure domain core in
`src/diamonds_are_forever/`; manuscript sections read numbers via `{{TOKEN}}`
injection and never state them in prose.
