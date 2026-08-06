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
from diamonds_are_forever.orbital_mirror import Satellite

with pytest.raises(ValueError):
    Satellite(altitude_km=-1.0, lat_deg=0.0, lon_deg=0.0)
```

(The class is `orbital_mirror.Satellite`; copy the import above with the snippet.)

## Real protocol discovery

```python
provider = load_provider("diamonds_are_forever", search_paths=[SRC])
assert provider.film == "diamonds_are_forever"
```

## Complete cycle enumeration (Johnson 1975)

```python
network = CasinoNetwork()
for source, target in (("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("d", "a")):
    network.add_transfer(source, target, 1.0)
# Both elementary circuits are reported: ('a','b','d','a') and ('a','c','d','a').
assert len(network.find_money_cycles()) == 2
```

## Live token gate (manuscript)

```python
variables = mv.generate_variables()
for source in sorted(MANUSCRIPT.glob("[0-9][0-9]_*.md")):
    used = set(_TOKEN_RE.findall(source.read_text()))
    assert not (used - set(variables))  # no unknown token
assert not (set(variables) - used_across_all)  # no orphan token (V4)
```
