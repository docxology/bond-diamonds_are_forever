# tests/ — AGENTS.md

Rules for tests in `diamonds_are_forever`.

- **No mocks**: never `unittest.mock` / `mocker.patch` / `MagicMock`. Real data
  + computation only (see `../docs/testing_philosophy.md`).
- Coverage-gated: `uv run pytest tests/ --cov=src --cov-fail-under=90`.
- Deterministic: fixed inputs, no RNG, no wall-clock assertions.
- Name files `test_<module>.py`; functions `test_*`.
- Keep the live manuscript-token cross-reference gate passing whenever
  `manuscript/NN_*.md` or `generate_variables()` changes.
