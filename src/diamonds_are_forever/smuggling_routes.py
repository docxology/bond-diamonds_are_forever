"""Risk-weighted smuggling-corridor routing (CONFLICT STONE deepening).

The provenance chain answers *who touched the goods*; this module answers
*which corridor the goods travel*. A smuggler moves a cargo of fixed value
through a directed network of corridors, each carrying a transport cost and a
seizure probability. The expected cost of a corridor is the transport cost plus
the probability-weighted loss of the cargo:

    expected_cost(corridor) = cost + p_seizure * cargo_value

:func:`least_risk_route` runs a deterministic Dijkstra over expected cost and
returns the route, its expected cost, and the survival probability
(``product(1 - p)`` over the route). :func:`naive_hops_route` returns the
fewest-hops BFS baseline in the *same* graph, so the optimality gap
(:func:`route_reduction`) is always non-negative.

Deterministic: heapq tie-breaks on an insertion counter, adjacency lists are
sorted, and there is no RNG.
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from itertools import pairwise

__all__ = [
    "Corridor",
    "RouteError",
    "SmugglingNetwork",
    "canonical_cargo_value_m",
    "canonical_corridors",
    "cost_of_path",
    "expected_cost",
    "least_risk_route",
    "naive_hops_route",
    "route_exposure",
    "route_reduction",
]


class RouteError(ValueError):
    """Raised for invalid corridor networks, endpoints, or unreachable routes."""


@dataclass(frozen=True)
class Corridor:
    """One directed smuggling corridor: transport cost (M USD) and seizure probability."""

    source: str
    target: str
    cost_m: float
    seizure_probability: float
    note: str = ""

    def __post_init__(self) -> None:
        for label, value in (("source", self.source), ("target", self.target)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Corridor.{label} must be a non-empty string")
        for number_label, number_value in (
            ("cost_m", self.cost_m),
            ("seizure_probability", self.seizure_probability),
        ):
            if not isinstance(number_value, (int, float)) or isinstance(number_value, bool):
                raise TypeError(f"Corridor.{number_label} must be a non-boolean number")
        if self.cost_m < 0:
            raise ValueError("Corridor.cost_m cannot be negative")
        if not 0.0 <= self.seizure_probability <= 1.0:
            raise ValueError("Corridor.seizure_probability must be within [0, 1]")


class SmugglingNetwork:
    """A directed corridor graph with at most one corridor per ordered pair."""

    def __init__(self) -> None:
        self._corridors: dict[tuple[str, str], Corridor] = {}

    def add_corridor(self, corridor: Corridor) -> None:
        """Register a corridor, rejecting self-loops and duplicates."""
        if not isinstance(corridor, Corridor):
            raise TypeError("corridor must be a Corridor")
        if corridor.source == corridor.target:
            raise RouteError("a corridor cannot start and end at the same node")
        key = (corridor.source, corridor.target)
        if key in self._corridors:
            raise RouteError(f"duplicate corridor {corridor.source!r} -> {corridor.target!r}")
        self._corridors[key] = corridor

    def corridors(self) -> tuple[Corridor, ...]:
        """All corridors in insertion order."""
        return tuple(self._corridors.values())

    def nodes(self) -> tuple[str, ...]:
        """All corridor endpoints, sorted alphabetically (deterministic)."""
        actors: set[str] = set()
        for corridor in self._corridors.values():
            actors.add(corridor.source)
            actors.add(corridor.target)
        return tuple(sorted(actors))

    def corridor(self, source: str, target: str) -> Corridor:
        """Look up a corridor, raising ``RouteError`` when absent."""
        try:
            return self._corridors[(source, target)]
        except KeyError:
            raise RouteError(f"no corridor from {source!r} to {target!r}") from None

    def adjacency(self) -> dict[str, tuple[str, ...]]:
        """Sorted successor lists per node (deterministic traversal order)."""
        outgoing: dict[str, list[str]] = {}
        for corridor in self._corridors.values():
            outgoing.setdefault(corridor.source, []).append(corridor.target)
        return {node: tuple(sorted(targets)) for node, targets in outgoing.items()}


def expected_cost(corridor: Corridor, cargo_value_m: float) -> float:
    """Transport cost plus probability-weighted cargo loss for one corridor."""
    if not isinstance(cargo_value_m, (int, float)) or isinstance(cargo_value_m, bool):
        raise TypeError("cargo_value_m must be a non-boolean number")
    if cargo_value_m < 0:
        raise ValueError("cargo_value_m cannot be negative")
    return float(corridor.cost_m + corridor.seizure_probability * cargo_value_m)


def cost_of_path(network: SmugglingNetwork, path: tuple[str, ...], cargo_value_m: float) -> float:
    """Total expected cost along a node path (raises on unknown corridors)."""
    if len(path) < 2:
        raise RouteError("a costed path needs at least two nodes")
    total = 0.0
    for left, right in pairwise(path):
        total += expected_cost(network.corridor(left, right), cargo_value_m)
    return total


def _check_endpoints(network: SmugglingNetwork, origin: str, destination: str) -> None:
    nodes = network.nodes()
    if origin not in nodes:
        raise RouteError(f"origin {origin!r} is not in the corridor network")
    if destination not in nodes:
        raise RouteError(f"destination {destination!r} is not in the corridor network")
    if origin == destination:
        raise RouteError("origin and destination must differ")


def least_risk_route(
    network: SmugglingNetwork,
    origin: str,
    destination: str,
    cargo_value_m: float,
) -> tuple[tuple[str, ...], float, float]:
    """Dijkstra over expected cost: returns ``(path, expected_cost_m, survival)``.

    Raises:
        RouteError: if endpoints are invalid or the destination is unreachable.
    """
    _check_endpoints(network, origin, destination)
    adjacency = network.adjacency()
    best_cost: dict[str, float] = {origin: 0.0}
    previous: dict[str, str] = {}
    survival: dict[str, float] = {origin: 1.0}
    heap: list[tuple[float, int, str]] = [(0.0, 0, origin)]
    counter = 1
    while heap:
        cost, _sequence, node = heapq.heappop(heap)
        if node == destination:
            break
        if cost > best_cost.get(node, float("inf")):
            continue  # stale heap entry
        for nxt in adjacency.get(node, ()):
            edge_cost = expected_cost(network.corridor(node, nxt), cargo_value_m)
            candidate = cost + edge_cost
            if candidate < best_cost.get(nxt, float("inf")):
                best_cost[nxt] = candidate
                previous[nxt] = node
                survival[nxt] = survival[node] * (
                    1.0 - network.corridor(node, nxt).seizure_probability
                )
                heapq.heappush(heap, (candidate, counter, nxt))
                counter += 1
    if destination not in best_cost:
        raise RouteError(f"no corridor path from {origin!r} to {destination!r}")
    path = [destination]
    node = destination
    while node != origin:
        node = previous[node]
        path.append(node)
    path.reverse()
    return tuple(path), best_cost[destination], survival[destination]


def naive_hops_route(network: SmugglingNetwork, origin: str, destination: str) -> tuple[str, ...]:
    """Fewest-hops route (BFS) — the naive smuggler baseline in the same graph."""
    _check_endpoints(network, origin, destination)
    adjacency = network.adjacency()
    previous: dict[str, str] = {}
    visited: set[str] = {origin}
    queue: deque[str] = deque([origin])
    while queue:
        node = queue.popleft()
        if node == destination:
            break
        for nxt in adjacency.get(node, ()):
            if nxt not in visited:
                visited.add(nxt)
                previous[nxt] = node
                queue.append(nxt)
    if destination not in visited:
        raise RouteError(f"no corridor path from {origin!r} to {destination!r}")
    path = [destination]
    node = destination
    while node != origin:
        node = previous[node]
        path.append(node)
    path.reverse()
    return tuple(path)


def route_exposure(survival_probability: float) -> float:
    """Seizure exposure of a route: ``1 - survival``."""
    return float(1.0 - survival_probability)


def route_reduction(naive_cost_m: float, optimal_cost_m: float) -> float:
    """Relative expected-cost reduction of the optimal route over the naive one."""
    if naive_cost_m <= 0:
        return 0.0
    return float((naive_cost_m - optimal_cost_m) / naive_cost_m)


def canonical_cargo_value_m() -> float:
    """The canonical CONFLICT STONE cargo value in millions of US dollars."""
    return 5.0


def canonical_corridors() -> SmugglingNetwork:
    """The canonical smuggling corridor network.

    The African leg offers an expensive, low-seizure charter flight, and the
    European leg offers a cheap ferry; the fewest-hops BFS baseline routes via
    the pricey London->Amsterdam ferry, while the expected-cost optimum detours
    through Paris — making the reduction metric genuinely non-trivial.
    """
    network = SmugglingNetwork()
    for source, target, cost, probability, note in (
        ("sierra_leone", "illicit_broker", 0.5, 0.60, "wildcat porter"),
        ("illicit_broker", "nairobi", 0.3, 0.50, "false-bottom truck"),
        ("nairobi", "london", 1.0, 0.35, "diplomatic pouch"),
        ("sierra_leone", "nairobi", 2.0, 0.25, "chartered cargo flight"),
        ("nairobi", "paris", 0.8, 0.30, "freight forwarder"),
        ("paris", "amsterdam", 0.4, 0.20, "ferry courier"),
        ("london", "amsterdam", 2.0, 0.15, "pricey channel ferry"),
        ("london", "new_york", 2.5, 0.12, "liner hold"),
        ("new_york", "las_vegas", 1.2, 0.10, "cross-country hire"),
        ("amsterdam", "las_vegas", 1.5, 0.18, "direct charter"),
    ):
        network.add_corridor(Corridor(source, target, cost, probability, note=note))
    return network
