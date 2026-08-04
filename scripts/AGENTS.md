# scripts/ — AGENTS.md

Rules for the thin orchestrators in `diamonds_are_forever`.

- **Thin only**: scripts orchestrate; business logic lives in
  `src/diamonds_are_forever/`. Do not grow analytic code here.
- **Bootstrap pattern**: each script inserts `<package root>/src` onto
  `sys.path` and imports from the core/adapter; keep the `# noqa: E402` on the
  post-bootstrap imports.
- **Deterministic**: scripts must not introduce RNG or wall-clock output.
- **Lint/type**: keep `ruff check` + `ruff format` + `mypy` clean on `scripts/`.
- Phase scripts exist per mission stage (brief/recon/plan/execute/debrief);
  `run_mission.py` composes the full flow.
