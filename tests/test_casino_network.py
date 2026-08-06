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
    # The three loops are the two-node strip loops and the three-node wash.
    assert set(cycles) == {
        ("caesars", "sands", "caesars"),
        ("dunes", "stardust", "dunes"),
        ("sahara", "tropicana", "whyte_house", "sahara"),
    }


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
    # A diamond (shared node) forces a circuit to share an intermediate node
    # between two loops; assert every reported cycle is a valid closed loop.
    network = CasinoNetwork()
    network.add_transfer("a", "b", 1.0)
    network.add_transfer("b", "c", 1.0)
    network.add_transfer("a", "c", 1.0)
    network.add_transfer("c", "b", 1.0)  # back edge -> cycle c->b->c
    cycles = network.find_money_cycles()
    assert cycles
    for cycle in cycles:
        assert cycle[0] == cycle[-1]
        assert len(set(cycle[:-1])) == len(cycle) - 1  # elementary


def test_closure_captures_only_cyclic_flow() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "b", 4.0)  # straight pass-through
    network.add_transfer("x", "y", 3.0)  # on cycle
    network.add_transfer("y", "x", 3.0)
    assert network.laundering_closure() == pytest.approx(6.0 / 10.0)


# ----------------------------------------------- complete circuit enumeration


def test_a_circuit_reentering_a_shared_done_node_is_not_lost() -> None:
    """The regression that motivated complete enumeration (Johnson, not DFS).

    Edges ``a->b, a->c, b->d, c->d, d->a`` form *two* elementary circuits,
    ``a->b->d->a`` and ``a->c->d->a``. A back-edge DFS finds only the first
    (``d`` is finished before ``c`` is explored), so a node re-entering an
    already-traversed branch is silently dropped — exactly the ``laundering
    closure`` under-report that complete enumeration exists to prevent.
    """
    network = CasinoNetwork()
    for source, target in (
        ("a", "b"),
        ("a", "c"),
        ("b", "d"),
        ("c", "d"),
        ("d", "a"),
    ):
        network.add_transfer(source, target, 1.0)
    assert set(network.find_money_cycles()) == {
        ("a", "b", "d", "a"),
        ("a", "c", "d", "a"),
    }
    # Both edges on the second circuit are laundering flow; closure reflects it.
    assert network.laundering_closure() == 1.0


def _reference_simple_cycles(network: CasinoNetwork) -> set[tuple[str, ...]]:
    """A complete, deliberately simple reference enumerator (dedupes rotations).

    Every simple directed cycle found by unrestricted DFS, reduced to a single
    canonical representative by rotation. This is exponential but exact, so it
    is the ground truth the Johnson enumerator is checked against.
    """

    def _canonical(cycle: tuple[str, ...]) -> tuple[str, ...]:
        body = list(cycle[:-1])
        least = min(body)
        index = body.index(least)
        rotated = body[index:] + body[:index]
        return tuple(rotated + [rotated[0]])

    adjacency: dict[str, list[str]] = {}
    for source, target, _amount in network.transfers():
        adjacency.setdefault(source, []).append(target)

    cycles: set[tuple[str, ...]] = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        path.append(node)
        for successor in adjacency.get(node, ()):
            if successor in path:
                start = path.index(successor)
                cycles.add(_canonical(tuple(path[start:] + [successor])))
            else:
                dfs(successor)
        path.pop()

    for node in network.casinos():
        dfs(node)
    return cycles


def test_enumerator_is_complete_against_a_reference() -> None:
    """The set of reported cycles equals the reference set, with no duplicates."""
    for edges in (
        # The overlapping-circuits regression.
        (("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("d", "a")),
        # A dense 3-node tournament.
        (("a", "b"), ("b", "a"), ("b", "c"), ("c", "a"), ("c", "b"), ("a", "c")),
        # A 5-node graph with nested circuits of several lengths.
        (
            ("a", "b"),
            ("b", "c"),
            ("c", "a"),
            ("c", "d"),
            ("d", "e"),
            ("e", "c"),
            ("a", "d"),
        ),
        # Two circuits sharing a node — forces Johnson's unblock to cascade
        # through a vertex reachable only via the blocked set.
        (("a", "b"), ("b", "c"), ("c", "a"), ("b", "d"), ("d", "b")),
        # A near-complete 3-node graph that provably triggers the recursive
        # unblock (a vertex finds a circuit while another vertex still points
        # to it from the blocked set).
        (("a", "b"), ("a", "c"), ("b", "a"), ("b", "c"), ("c", "b")),
        # A near-complete 5-node graph that exercises both arms of Johnson's
        # blocked-set unblock (cascade through a blocked vertex *and* skip a
        # successor that is already unblocked).
        (
            ("a", "b"),
            ("a", "c"),
            ("d", "b"),
            ("b", "e"),
            ("b", "a"),
            ("e", "a"),
            ("a", "d"),
            ("d", "e"),
            ("c", "d"),
            ("b", "d"),
            ("c", "a"),
            ("d", "a"),
            ("d", "c"),
            ("e", "d"),
            ("c", "e"),
            ("e", "c"),
            ("c", "b"),
            ("b", "c"),
        ),
    ):
        network = CasinoNetwork()
        for source, target in edges:
            network.add_transfer(source, target, 1.0)
        reported = set(network.find_money_cycles())
        reference = _reference_simple_cycles(network)
        assert reported == reference, (edges, reported, reference)
        assert len(reported) == len(network.find_money_cycles())  # no duplicate rows


def test_reported_cycles_are_distinct() -> None:
    """Uniqueness is structural — a dense graph must not yield duplicate rows."""
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
    # Canonical network is unchanged.
    assert len(canonical_network().find_money_cycles()) == 3


def test_diamond_graph_with_no_cycles_returns_empty() -> None:
    network = CasinoNetwork()
    network.add_transfer("a", "shared", 1.0)
    network.add_transfer("b", "shared", 1.0)
    network.add_transfer("b", "zulu", 1.0)
    network.add_transfer("shared", "sink", 1.0)
    assert network.find_money_cycles() == ()
    assert network.laundering_closure() == 0.0


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
