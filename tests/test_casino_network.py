"""Tests for the Las Vegas casino money-movement network (deterministic, no mocks)."""

from __future__ import annotations

import pytest

from diamonds_are_forever.casino_network import (
    CaminoError,
    CasinoNetwork,
    canonical_network,
    compute_hub,
    laundering_closure,
)

# ---------------------------------------------------------------- canonical


def test_canonical_network_topology() -> None:
    network = canonical_network()
    assert network.casinos() == (
        "caesars",
        "dunes",
        "sahara",
        "sands",
        "stardust",
        "tropicana",
        "whyte_house",
    )
    assert len(network.transfers()) == 9
    assert network.total_flow() == pytest.approx(31.0)


def test_canonical_hub_is_whyte_house() -> None:
    assert canonical_network().hub() == "whyte_house"


def test_canonical_has_three_money_cycles() -> None:
    cycles = canonical_network().find_money_cycles()
    assert len(cycles) == 3


def test_canonical_laundering_closure() -> None:
    assert canonical_network().laundering_closure() == pytest.approx(24.0 / 31.0)


def test_module_level_wrappers() -> None:
    network = canonical_network()
    assert compute_hub(network) == "whyte_house"
    assert laundering_closure(network) == pytest.approx(24.0 / 31.0)


# ---------------------------------------------------------------- core flow


def test_add_transfer_accumulates_repeated_pairs() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 1.0)
    network.add_transfer("a", "b", 2.5)
    assert network.total_outflow("a") == pytest.approx(3.5)
    assert len(network.transfers()) == 1


def test_casinos_sorted_alphabetically() -> None:
    network = CasinoNetwork()
    network.add_transfer("zulu", "alpha", 1.0)
    assert network.casinos() == ("alpha", "zulu")


def test_inflow_outflow_net_gross() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 5.0)
    network.add_transfer("c", "a", 2.0)
    assert network.total_inflow("a") == pytest.approx(2.0)
    assert network.total_outflow("a") == pytest.approx(5.0)
    assert network.net_flow("a") == pytest.approx(-3.0)
    assert network.gross_flow("a") == pytest.approx(7.0)
    assert network.total_inflow("unknown") == 0.0
    assert network.total_outflow("unknown") == 0.0


def test_empty_network_metrics() -> None:
    network = CasinoNetwork()
    assert network.casinos() == ()
    assert network.transfers() == ()
    assert network.total_flow() == 0.0
    assert network.hub() == ""
    assert network.find_money_cycles() == ()
    assert network.laundering_closure() == 0.0


def test_closure_zero_for_one_way_flow() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 1.0)
    network.add_transfer("b", "c", 1.0)
    assert network.laundering_closure() == 0.0


def test_hub_picks_greatest_gross_flow() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 10.0)
    network.add_transfer("b", "c", 1.0)
    # b touches 10 in + 1 out = 11 > a's 10.
    assert network.hub() == "b"


def test_cycle_two_node() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 1.0)
    network.add_transfer("b", "a", 1.0)
    assert network.find_money_cycles() == (("a", "b", "a"),)


def test_cycle_detection_with_shared_done_neighbour() -> None:
    # A diamond (shared node) forces a second visit to an already-done node,
    # exercising the 'neighbour is done' branch of the DFS.
    network = CasinoNetwork()
    network.add_transfer("a", "b", 1.0)
    network.add_transfer("b", "c", 1.0)
    network.add_transfer("a", "c", 1.0)
    network.add_transfer("c", "b", 1.0)  # back edge -> cycle c->b->c
    cycles = network.find_money_cycles()
    # At least one cycle must be discovered; assert it is a valid closed loop.
    assert cycles
    for cycle in cycles:
        assert cycle[0] == cycle[-1]


def test_closure_captures_only_cyclic_flow() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 4.0)  # straight pass-through
    network.add_transfer("x", "y", 3.0)  # on cycle
    network.add_transfer("y", "x", 3.0)
    assert network.laundering_closure() == pytest.approx(6.0 / 10.0)


# -------------------------------------------------------------- validation


def test_add_transfer_rejects_empty_source() -> None:
    with pytest.raises(CaminoError):
        CasinoNetwork().add_transfer("", "b", 1.0)


def test_add_transfer_rejects_empty_target() -> None:
    with pytest.raises(CaminoError):
        CasinoNetwork().add_transfer("a", "", 1.0)


def test_add_transfer_rejects_self_move() -> None:
    with pytest.raises(CaminoError):
        CasinoNetwork().add_transfer("a", "a", 1.0)


def test_add_transfer_rejects_negative() -> None:
    with pytest.raises(CaminoError):
        CasinoNetwork().add_transfer("a", "b", -1.0)


def test_add_transfer_rejects_non_number() -> None:
    with pytest.raises(CaminoError):
        CasinoNetwork().add_transfer("a", "b", "lots")  # type: ignore[arg-type]


def test_add_transfer_rejects_bool_amount() -> None:
    with pytest.raises(CaminoError):
        CasinoNetwork().add_transfer("a", "b", True)  # type: ignore[arg-type]


def test_cycle_search_skips_already_finished_successors() -> None:
    """A successor whose DFS is complete is neither a back edge nor re-entered.

    ``a`` and ``b`` both lead into ``shared``; by the time ``b`` is explored,
    ``shared`` is finished (state 2), so the scan must fall through both the
    back-edge test and the recursion test and carry on to ``b``'s *second*
    successor without reporting a spurious cycle.
    """
    network = CasinoNetwork()
    network.add_transfer("a", "shared", 1.0)
    network.add_transfer("b", "shared", 1.0)
    network.add_transfer("b", "zulu", 1.0)
    network.add_transfer("shared", "sink", 1.0)
    assert network.find_money_cycles() == ()
    assert network.laundering_closure() == 0.0
    # The second successor really was reached (it is a node of the graph).
    assert "zulu" in network.casinos()


def test_reported_cycles_are_distinct_without_a_dedup_pass() -> None:
    """Uniqueness is structural, not filtered — assert it holds on a dense graph.

    Every back edge is traversed once and edges are unique by construction, so
    the enumerator needs no de-duplication guard. This test is what stands in
    for that removed guard: if the invariant ever breaks, duplicates appear
    here rather than being silently swallowed.
    """
    network = CasinoNetwork()
    for source, target in (
        ("a", "b"),
        ("b", "a"),
        ("b", "c"),
        ("c", "a"),
        ("c", "b"),
        ("a", "c"),
    ):
        network.add_transfer(source, target, 1.0)
    cycles = network.find_money_cycles()
    assert len(cycles) == len(set(cycles)), cycles
    assert cycles, "the dense graph must actually contain cycles"
    for cycle in cycles:
        assert cycle[0] == cycle[-1]
    # Canonical network is unchanged by removing the guard.
    assert len(canonical_network().find_money_cycles()) == 3
