# scripts/ — CONVENTIONS.md

Conventions for the thin orchestrators.

- One CLI = one small top-level `main() -> int` raising `SystemExit(main())`.
- Use `argparse` where flags are needed; keep defaults deterministic.
- `sys.path` bootstrap first, then imports; annotate with `# noqa: E402` when
  the import follows the bootstrap.
- Match `src/` style: 100-char lines, `ruff format`, full annotations.
- Exit code 0 on success; propagate errors so CI/pytest can assert on them.
