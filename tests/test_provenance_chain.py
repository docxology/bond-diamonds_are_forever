"""Tests for the conflict-diamond provenance chain (deterministic, no mocks)."""

from __future__ import annotations

import pytest

from diamonds_are_forever.provenance_chain import (
    ChainInconsistencyError,
    CustodyTransfer,
    break_points,
    build_chain,
    canonical_transfers,
    is_conflict_free,
    provenance_coverage,
    trace_origin,
    validate_transfers,
)


def _chain(*specs: tuple[str, str, bool]) -> tuple[CustodyTransfer, ...]:
    return tuple(CustodyTransfer(source=s, target=t, recorded=r) for s, t, r in specs)


# ---------------------------------------------------------------- canonical


def test_canonical_route_has_two_break_points() -> None:
    transfers = canonical_transfers()
    assert len(transfers) == 5
    assert break_points(transfers) == (0, 1)  # the two smuggling hops are undocumented


def test_canonical_coverage_is_three_fifths() -> None:
    assert provenance_coverage(canonical_transfers()) == pytest.approx(0.6)


def test_canonical_is_not_conflict_free() -> None:
    assert is_conflict_free(canonical_transfers()) is False


def test_canonical_chain_builds() -> None:
    assert len(build_chain(canonical_transfers())) == 5


def test_canonical_origin_trace_full_path() -> None:
    assert trace_origin(canonical_transfers(), "las_vegas_fence") == (
        "sierra_leone_mine",
        "illicit_broker",
        "nairobi_courier",
        "london_dealer",
        "amsterdam_contact",
        "las_vegas_fence",
    )


def test_origin_trace_stops_at_intermediate_node() -> None:
    assert trace_origin(canonical_transfers(), "london_dealer") == (
        "sierra_leone_mine",
        "illicit_broker",
        "nairobi_courier",
        "london_dealer",
    )


# ------------------------------------------------------------- validation


def test_validate_transfers_rejects_non_sequence() -> None:
    with pytest.raises(TypeError):
        validate_transfers(("a", "b", "c"))  # strings, not a sequence of transfers


def test_validate_transfers_rejects_non_transfer_entry() -> None:
    with pytest.raises(TypeError):
        validate_transfers([("sierra", "broker", True)])


def test_transfer_rejects_empty_source() -> None:
    with pytest.raises(ValueError):
        CustodyTransfer(source="  ", target="broker", recorded=True)


def test_transfer_rejects_empty_gem() -> None:
    with pytest.raises(ValueError):
        CustodyTransfer(source="sierra", target="broker", recorded=True, gem="")


def test_transfer_rejects_non_bool_recorded() -> None:
    with pytest.raises(TypeError):
        CustodyTransfer(source="sierra", target="broker", recorded="yes")  # type: ignore[arg-type]


def test_transfer_accepts_notes() -> None:
    transfer = CustodyTransfer("sierra", "broker", False, note="wildcat")
    assert transfer.note == "wildcat"


# -------------------------------------------------------------- build_chain


def test_build_chain_rejects_empty() -> None:
    with pytest.raises(ChainInconsistencyError):
        build_chain([])


def test_build_chain_rejects_self_loop() -> None:
    with pytest.raises(ChainInconsistencyError):
        build_chain(_chain(("a", "a", True)))


def test_build_chain_rejects_discontinuity() -> None:
    with pytest.raises(ChainInconsistencyError):
        build_chain(_chain(("a", "b", True), ("c", "d", True)))


def test_build_chain_rejects_cycle() -> None:
    with pytest.raises(ChainInconsistencyError):
        build_chain(_chain(("a", "b", True), ("b", "a", True)))


def test_build_chain_single_transfer() -> None:
    assert len(build_chain(_chain(("a", "b", True)))) == 1


# ------------------------------------------------------------ pure functions


def test_provenance_coverage_is_zero_for_empty_chain() -> None:
    assert provenance_coverage([]) == 0.0


def test_break_points_returns_indices_of_undocumented() -> None:
    transfers = _chain(("a", "b", False), ("b", "c", True), ("c", "d", False))
    assert break_points(transfers) == (0, 2)


def test_conflict_free_true_when_all_documented() -> None:
    assert is_conflict_free(_chain(("a", "b", True), ("b", "c", True))) is True


def test_trace_origin_rejects_empty_node() -> None:
    with pytest.raises(ValueError):
        trace_origin(canonical_transfers(), "")


def test_trace_origin_rejects_unknown_node() -> None:
    with pytest.raises(ChainInconsistencyError):
        trace_origin(canonical_transfers(), "casino")


def test_trace_origin_rejects_empty_chain() -> None:
    with pytest.raises(ChainInconsistencyError):
        trace_origin([], "a")


def test_validate_rejects_a_non_sequence() -> None:
    """A bare CustodyTransfer (not wrapped in a sequence) must fail loudly."""
    with pytest.raises(TypeError, match="must be a sequence"):
        validate_transfers(CustodyTransfer("a", "b", recorded=True))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a sequence"):
        break_points("not-a-chain")  # type: ignore[arg-type]


def test_trace_origin_to_the_origin_is_a_single_element_path() -> None:
    """Regression: the scan used to fall through and return the whole chain.

    The origin is never any handoff's ``target`` in an acyclic chain, so the
    break condition never fires for it. The bug was silent — it returned a
    well-formed path that simply answered a different question.
    """
    chain = canonical_transfers()
    origin = chain[0].source
    assert trace_origin(chain, origin) == (origin,)
    # The far end still returns the full route, so the fix is not a blanket
    # short-circuit.
    assert trace_origin(chain, chain[-1].target)[0] == origin
    assert trace_origin(chain, chain[-1].target)[-1] == chain[-1].target
    assert len(trace_origin(chain, chain[-1].target)) == len(chain) + 1


def test_trace_origin_stops_at_an_intermediate_node() -> None:
    chain = canonical_transfers()
    midpoint = chain[1].target
    path = trace_origin(chain, midpoint)
    assert path == (chain[0].source, chain[0].target, midpoint)
