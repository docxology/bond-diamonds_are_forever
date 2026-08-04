# tests/ — PATTERNS.md

Reusable test patterns for the CONFLICT STONE suite.

## Determinism proof

```python
def test_debrief_is_deterministic():
    provider = MissionProvider()
    first = provider.debrief(provider.execute(provider.plan(provider.brief())))
    second = provider.debrief(provider.execute(provider.plan(provider.brief())))
    assert first.outcome.provenance.input_hash == second.outcome.provenance.input_hash
    assert first.lessons == second.lessons
```

## Validation branch

```python
with pytest.raises(ValueError):
    OrbitalsSatellite(altitude_km=-1.0, lat_deg=0.0, lon_deg=0.0)
```

## Real protocol discovery

```python
provider = load_provider("diamonds_are_forever", search_paths=[SRC])
assert provider.film == "diamonds_are_forever"
```

## Live token gate (manuscript)

```python
variables = mv.generate_variables()
for source in sorted(MANUSCRIPT.glob("[0-9][0-9]_*.md")):
    used = set(_TOKEN_RE.findall(source.read_text()))
    assert not (used - set(variables))
```
