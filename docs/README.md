# docs/ — diamonds_are_forever (CONFLICT STONE · DIAMOND NET)

Agent- and human-facing documentation for the BOND film package *Diamonds Are
Forever (1971)*. Four documents, each answering a different question.

| File | Answers |
|---|---|
| `README.md` | This index — what is here and which file to open |
| `agent_instructions.md` | *What am I allowed to do?* Scope, guardrails, the frozen protocol surface, the checklist before changing code |
| `architecture.md` | *How does it work?* Every module in `src/` and what it computes, the layer contract, how `mission.py` satisfies the frozen `MissionProvider`, determinism, and two numerical traps |
| `testing_philosophy.md` | *How do I test it?* The no-mock / real-data / determinism doctrine, the file map, oracle discipline, and the tests that stand in for deliberately removed guards |
| `AGENTS.md` | Directory-level rules for editing these documents |

## Where to start

- **Changing an algorithm** → `architecture.md` for the module's contract, then
  `testing_philosophy.md` before touching its tests.
- **Touching `mission.py`** → `agent_instructions.md`, *The frozen surface*.
  Its shape is consumed by `bond-cli`, the coordinator, and the orchestrator.
- **Adding or changing a number in the manuscript** → `agent_instructions.md`,
  *Before changing code*. Numbers are never written into prose.

## Related documents outside this directory

| Path | Holds |
|---|---|
| `../README.md` | Package overview, module table, install and verify commands |
| `../AGENTS.md` | Package-root agent rules and the layer contract summary |
| `../TODO.md` | Remaining work |
| `../manuscript/SYNTAX.md` | Manuscript token and figure protocol |
| `../data/claim_ledger.yaml` | Each headline number and the exact call that produces it |
| `../domain_profile.yaml` | The declared review gates and expected artifacts |

## The standing rule

The authoritative source for every metric is the pure domain core in
`src/diamonds_are_forever/`. Manuscript sections read numbers via `{{TOKEN}}`
injection and never state them in prose — including model constants such as
thresholds, critical values, and requirements, which are exported as named
constants from their owning module and reach the prose as tokens.
