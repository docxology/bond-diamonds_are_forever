"""V1 — bind every row of ``data/claim_ledger.yaml`` to its live ``source`` call.

The ledger is the package's contract with the manuscript: each headline claim
is a number the prose rests on. Any row whose ``source`` stops evaluating to
its ``value`` (because a canonical dataset moved) must fail here, and a new row
added without a source must fail too — so a claim can never be added unbound.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from diamonds_are_forever import (
    beam_physics,
    benford_audit,
    casino_network,
    lot_forensics,
    orbital_mirror,
    provenance_chain,
    smuggling_routes,
)

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "claim_ledger.yaml"

_MODULES = (
    provenance_chain,
    smuggling_routes,
    lot_forensics,
    casino_network,
    benford_audit,
    beam_physics,
    orbital_mirror,
)

#: Namespace in which each claim ``source`` is evaluated: the seven pure modules
#: by short name, plus their public functions/constants merged by bare name.
_NAMESPACE: dict[str, object] = {}
for _module in _MODULES:
    _short = _module.__name__.rsplit(".", 1)[-1]
    _NAMESPACE[_short] = _module
    for _name, _obj in vars(_module).items():
        if not _name.startswith("_"):
            _NAMESPACE.setdefault(_name, _obj)

# The ids the ledger is expected to carry. Asserting the exact set means a new
# row cannot be added without the test noticing (and an id cannot be dropped).
_EXPECTED_IDS = frozenset(
    {
        "provenance.transfers",
        "provenance.breakpoints",
        "provenance.coverage",
        "smuggling.corridors",
        "smuggling.route",
        "smuggling.expected_cost_m",
        "smuggling.survival",
        "smuggling.reduction",
        "forensics.anomalies",
        "forensics.verdict",
        "casino.casinos",
        "casino.laundering_closure",
        "benford.transactions",
        "benford.chi_square",
        "benford.verdict",
        "benford.legitimate_transactions",
        "benford.legitimate_chi_square",
        "benford.legitimate_verdict",
        "beam.spot_radius_m",
        "beam.concentration",
        "beam.min_mirror_diameter_m",
    }
)


def _assert_claim(claim_id: str, evaluated: object, expected: object) -> None:
    if isinstance(expected, int):
        assert isinstance(evaluated, int), (claim_id, evaluated)
        assert evaluated == expected, claim_id
    elif isinstance(expected, float):
        # Stored values are human-readable rounded figures (e.g. 0.1614, 42.7)
        # while the source yields full precision; a relative tolerance of 1%
        # absorbs rounding while still flagging a claim that has genuinely
        # drifted from its live computation.
        assert evaluated == pytest.approx(expected, rel=1e-2), claim_id
    elif isinstance(expected, str):
        assert evaluated == expected, claim_id
    else:  # claim values are contractually int/float/str
        raise TypeError(f"{claim_id}: unsupported claim value type {type(expected).__name__}")


def _load_claims() -> list[dict]:
    data = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return list(data["claims"])


def test_claim_ledger_has_all_expected_ids() -> None:
    ids = {claim["id"] for claim in _load_claims()}
    assert ids == _EXPECTED_IDS, ids ^ _EXPECTED_IDS


def test_every_claim_recomputes_from_its_source() -> None:
    for claim in _load_claims():
        evaluated = eval(claim["source"], dict(_NAMESPACE))  # config-controlled, namespaced
        _assert_claim(str(claim["id"]), evaluated, claim["value"])
