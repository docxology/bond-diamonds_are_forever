"""Tests for risk-weighted smuggling-corridor routing (deterministic, no mocks)."""

from __future__ import annotations

import pytest

from diamonds_are_forever.smuggling_routes import (
    Corridor,
    RouteError,
    SmugglingNetwork,
    canonical_cargo_value_m,
    canonical_corridors,
    cost_of_path,
    expected_cost,
    least_risk_route,
    naive_hops_route,
    route_exposure,
    route_reduction,
)


def _network() -> SmugglingNetwork:
    return canonical_corridors()


# ---------------------------------------------------------------- canonical


def test_canonical_network_shape() -> None:
    network = _network()
    assert len(network.corridors()) == 10
    assert network.nodes() == (
        "amsterdam",
        "illicit_broker",
        "las_vegas",
        "london",
        "nairobi",
        "new_york",
        "paris",
        "sierra_leone",
    )
    assert canonical_cargo_value_m() == 5.0


def test_canonical_least_risk_route() -> None:
    network = _network()
    route, cost, survival = least_risk_route(
        network, "sierra_leone", "las_vegas", canonical_cargo_value_m()
    )
    assert route == ("sierra_leone", "nairobi", "paris", "amsterdam", "las_vegas")
    assert cost == pytest.approx(9.35)
    assert survival == pytest.approx(0.3444, abs=1e-4)


def test_canonical_naive_baseline_differs_from_optimum() -> None:
    network = _network()
    naive = naive_hops_route(network, "sierra_leone", "las_vegas")
    route, _cost, _survival = least_risk_route(
        network, "sierra_leone", "las_vegas", canonical_cargo_value_m()
    )
    assert naive == ("sierra_leone", "nairobi", "london", "amsterdam", "las_vegas")
    assert naive != route
    naive_cost = cost_of_path(network, naive, canonical_cargo_value_m())
    assert naive_cost == pytest.approx(11.15)


def test_canonical_reduction_is_positive_and_bounded() -> None:
    network = _network()
    cargo = canonical_cargo_value_m()
    _route, cost, _survival = least_risk_route(network, "sierra_leone", "las_vegas", cargo)
    naive_cost = cost_of_path(
        network, naive_hops_route(network, "sierra_leone", "las_vegas"), cargo
    )
    reduction = route_reduction(naive_cost, cost)
    assert reduction == pytest.approx(0.1614, abs=1e-3)
    assert 0.0 <= reduction <= 1.0
    assert cost <= naive_cost  # optimality within the same graph


def test_canonical_exposure_complements_survival() -> None:
    _route, _cost, survival = least_risk_route(
        _network(), "sierra_leone", "las_vegas", canonical_cargo_value_m()
    )
    assert route_exposure(survival) == pytest.approx(1.0 - survival)


def test_route_determinism() -> None:
    network = _network()
    cargo = canonical_cargo_value_m()
    first = least_risk_route(network, "sierra_leone", "las_vegas", cargo)
    second = least_risk_route(network, "sierra_leone", "las_vegas", cargo)
    assert first == second


# ----------------------------------------------------------------- Corridor


def test_corridor_rejects_empty_source() -> None:
    with pytest.raises(ValueError):
        Corridor("", "b", 1.0, 0.1)


def test_corridor_rejects_empty_target() -> None:
    with pytest.raises(ValueError):
        Corridor("a", "", 1.0, 0.1)


def test_corridor_rejects_non_number_cost() -> None:
    with pytest.raises(TypeError):
        Corridor("a", "b", "pricey", 0.1)  # type: ignore[arg-type]


def test_corridor_rejects_negative_cost() -> None:
    with pytest.raises(ValueError):
        Corridor("a", "b", -1.0, 0.1)


def test_corridor_rejects_probability_below_zero() -> None:
    with pytest.raises(ValueError):
        Corridor("a", "b", 1.0, -0.1)


def test_corridor_rejects_probability_above_one() -> None:
    with pytest.raises(ValueError):
        Corridor("a", "b", 1.0, 1.1)


# ------------------------------------------------------------ network ops


def test_add_corridor_rejects_self_loop() -> None:
    with pytest.raises(RouteError):
        SmugglingNetwork().add_corridor(Corridor("a", "a", 1.0, 0.1))


def test_add_corridor_rejects_duplicate() -> None:
    network = SmugglingNetwork()
    network.add_corridor(Corridor("a", "b", 1.0, 0.1))
    with pytest.raises(RouteError):
        network.add_corridor(Corridor("a", "b", 2.0, 0.2))


def test_add_corridor_rejects_non_corridor() -> None:
    with pytest.raises(TypeError):
        SmugglingNetwork().add_corridor(("a", "b", 1.0, 0.1))  # type: ignore[arg-type]


def test_corridors_preserve_insertion_order() -> None:
    network = SmugglingNetwork()
    network.add_corridor(Corridor("z", "y", 1.0, 0.1))
    network.add_corridor(Corridor("a", "b", 1.0, 0.1))
    assert [c.source for c in network.corridors()] == ["z", "a"]


def test_corridor_lookup_missing_raises() -> None:
    with pytest.raises(RouteError):
        _network().corridor("las_vegas", "sierra_leone")  # no such reverse corridor


def test_adjacency_sorted() -> None:
    assert _network().adjacency()["nairobi"] == ("london", "paris")


# ---------------------------------------------------------------- expected


def test_expected_cost_includes_seizure_exposure() -> None:
    corridor = Corridor("a", "b", 2.0, 0.5)
    assert expected_cost(corridor, 10.0) == pytest.approx(7.0)


def test_expected_cost_rejects_negative_cargo() -> None:
    with pytest.raises(ValueError):
        expected_cost(Corridor("a", "b", 1.0, 0.1), -1.0)


def test_expected_cost_rejects_bad_cargo_type() -> None:
    with pytest.raises(TypeError):
        expected_cost(Corridor("a", "b", 1.0, 0.1), "valuable")  # type: ignore[arg-type]


def test_cost_of_path_requires_two_nodes() -> None:
    with pytest.raises(RouteError):
        cost_of_path(_network(), ("sierra_leone",), 5.0)


def test_cost_of_path_sums_edges() -> None:
    network = _network()
    naive = naive_hops_route(network, "sierra_leone", "las_vegas")
    assert cost_of_path(network, naive, 5.0) == pytest.approx(11.15)


# -------------------------------------------------------------- route errors


def test_least_risk_unknown_origin() -> None:
    with pytest.raises(RouteError):
        least_risk_route(_network(), "nowhere", "las_vegas", 5.0)


def test_least_risk_unknown_destination() -> None:
    with pytest.raises(RouteError):
        least_risk_route(_network(), "sierra_leone", "nowhere", 5.0)


def test_least_risk_same_endpoints() -> None:
    with pytest.raises(RouteError):
        least_risk_route(_network(), "london", "london", 5.0)


def test_least_risk_unreachable() -> None:
    network = SmugglingNetwork()
    network.add_corridor(Corridor("a", "b", 1.0, 0.1))
    network.add_corridor(Corridor("c", "d", 1.0, 0.1))
    with pytest.raises(RouteError):
        least_risk_route(network, "a", "d", 5.0)


def test_naive_hops_unreachable() -> None:
    network = SmugglingNetwork()
    network.add_corridor(Corridor("a", "b", 1.0, 0.1))
    network.add_corridor(Corridor("c", "d", 1.0, 0.1))
    with pytest.raises(RouteError):
        naive_hops_route(network, "a", "d")


def test_route_reduction_zero_for_empty_baseline() -> None:
    assert route_reduction(0.0, 0.0) == 0.0
    assert route_reduction(-1.0, 0.0) == 0.0


def test_dijkstra_discards_stale_heap_entries() -> None:
    """A node relaxed twice leaves a superseded heap entry that must be skipped.

    ``mid`` is reached first via the cheap-prefix/expensive-suffix leg through
    ``alpha`` (total 11), then improved to 3 via ``bravo``, so two entries for
    ``mid`` coexist in the heap. The long ``mid -> end`` leg (cost 20) keeps the
    destination behind the stale entry in pop order, so the stale ``(11, mid)``
    entry really is popped and must be discarded rather than re-expanded.
    """
    network = SmugglingNetwork()
    for source, target, cost in (
        ("origin", "alpha", 1.0),
        ("origin", "bravo", 2.0),
        ("alpha", "mid", 10.0),
        ("bravo", "mid", 1.0),
        ("mid", "end", 20.0),
    ):
        network.add_corridor(Corridor(source, target, cost, 0.0))
    path, cost, survival = least_risk_route(network, "origin", "end", 1.0)
    assert path == ("origin", "bravo", "mid", "end")
    assert cost == pytest.approx(23.0)
    assert survival == pytest.approx(1.0)


def test_route_reduction_is_zero_for_a_degenerate_baseline() -> None:
    """A free naive route cannot produce a negative or infinite reduction."""
    assert route_reduction(0.0, 0.0) == 0.0
    assert route_reduction(-1.0, 5.0) == 0.0
