"""Las Vegas casino network analysis: inter-casino money movement.

CONFLICT STONE traces how diamond-smuggling proceeds are laundered through the
Las Vegas casino ecosystem. Money moves casino-to-casino along a directed,
weighted multigraph; analysis surfaces gross flow, net positions, circular
(laundering) paths, and the network's hub casino.

Money cycles are enumerated *completely* — every elementary circuit, once —
with Johnson's 1975 algorithm rather than a back-edge DFS, so a graph with
overlapping circuits cannot silently under-report its own laundering loops.

Everything is deterministic: amounts are exact ``float`` values accumulated in
insertion order, iteration follows insertion order, and there is no RNG.
"""

from __future__ import annotations

from itertools import pairwise

__all__ = [
    "CaminoError",
    "CasinoNetwork",
    "canonical_network",
    "compute_hub",
    "laundering_closure",
]


class CaminoError(ValueError):
    """Raised on invalid money-movement inputs."""


class CasinoNetwork:
    """A directed, weighted inter-casino money-movement graph.

    Edges are keyed by ``(source, target)``; re-adding the same pair
    accumulates the amount (a real ledger must total repeated wires).
    """

    def __init__(self) -> None:
        self._edges: dict[tuple[str, str], float] = {}

    def add_transfer(self, source: str, target: str, amount: float) -> None:
        """Record a money transfer between casinos, accumulating repeated pairs."""
        if not isinstance(source, str) or not source.strip():
            raise CaminoError("source must be a non-empty string")
        if not isinstance(target, str) or not target.strip():
            raise CaminoError("target must be a non-empty string")
        if target == source:
            raise CaminoError("money cannot move to the same casino")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise CaminoError("amount must be a non-boolean number")
        if amount < 0:
            raise CaminoError("amount cannot be negative")
        key = (source, target)
        self._edges[key] = self._edges.get(key, 0.0) + float(amount)

    def casinos(self) -> tuple[str, ...]:
        """All casino names, sorted alphabetically (deterministic)."""
        actors: set[str] = set()
        for source, target in self._edges:
            actors.add(source)
            actors.add(target)
        return tuple(sorted(actors))

    def transfers(self) -> tuple[tuple[str, str, float], ...]:
        """All ``(source, target, amount)`` edges in insertion order."""
        return tuple((s, t, amt) for (s, t), amt in self._edges.items())

    def total_inflow(self, casino: str) -> float:
        """Total money flowing into ``casino`` (0.0 for an unknown casino)."""
        return float(sum(amount for (_, target), amount in self._edges.items() if target == casino))

    def total_outflow(self, casino: str) -> float:
        """Total money flowing out of ``casino`` (0.0 for an unknown casino)."""
        return float(sum(amount for (source, _), amount in self._edges.items() if source == casino))

    def net_flow(self, casino: str) -> float:
        """Net ledger position of ``casino`` (inflow minus outflow)."""
        return self.total_inflow(casino) - self.total_outflow(casino)

    def total_flow(self) -> float:
        """Sum of every recorded transfer."""
        return sum(self._edges.values())

    def gross_flow(self, casino: str) -> float:
        """Total money touching ``casino`` (inflow plus outflow)."""
        return self.total_inflow(casino) + self.total_outflow(casino)

    def hub(self) -> str:
        """The casino with the greatest gross flow; ties break to the alphabetically first."""
        actors = self.casinos()
        best = ""
        best_flow = -1.0
        for actor in actors:
            flow = self.gross_flow(actor)
            if flow > best_flow:
                best, best_flow = actor, flow
        return best

    def find_money_cycles(self) -> tuple[tuple[str, ...], ...]:
        """Every distinct directed money cycle (laundering loop), exactly once.

        This is a *complete* elementary-circuit enumeration (Johnson 1975,
        following the classical statement of Tarjan 1973): each simple directed
        cycle is reported exactly once, never as a rotation or reverse of
        itself. Completeness matters because closures and cycle counts are only
        well-defined when the enumerator cannot drop an overlapping circuit — a
        graph where one circuit re-enters an already-traversed node otherwise
        under-reports its own topology. The canonical network (three
        edge-disjoint loops) yields exactly three circuits by either rule; the
        guarantee this method adds is that *any* graph is enumerated fully.

        Cycles are reported as ``(n0, n1, ..., n0)`` in Johnson's canonical
        order — each starts at the least node in the cycle and follows the
        graph's sorted adjacency, so the result is deterministic.
        """
        nodes = self.casinos()
        index = {node: i for i, node in enumerate(nodes)}
        adjacency: list[list[int]] = [[] for _ in range(len(nodes))]
        for source, target in self._edges:
            adjacency[index[source]].append(index[target])
        for successors in adjacency:
            successors.sort()
        return _johnson_circuits(adjacency, nodes)

    def laundering_closure(self) -> float:
        """Fraction of total flow that sits on a money cycle (0.0 if no flow).

        A closure of 1.0 means every transfer is part of a circular laundering
        loop; 0.0 means money only ever moves one way (straight pass-through).
        """
        total = self.total_flow()
        if total <= 0:
            return 0.0
        cycle_edges: set[tuple[str, str]] = set()
        for cycle in self.find_money_cycles():
            for left, right in pairwise(cycle):
                cycle_edges.add((left, right))
        on_cycle = sum(
            amount
            for (source, target), amount in self._edges.items()
            if (source, target) in cycle_edges
        )
        return on_cycle / total


def _strongly_connected_component_starting_at(
    adjacency: list[list[int]], active: set[int], start: int
) -> set[int]:
    """The strongly connected component of ``start`` in ``adjacency`` restricted to ``active``.

    ``active`` is the vertex set of the induced subgraph being considered;
    ``start`` is the minimum-index vertex of that subgraph. The component is
    the intersection of the vertices reachable from ``start`` with the vertices
    that can reach ``start``. The graphs involved here are tiny (the canonical
    network has seven nodes), so a straightforward reachability pair is
    adequate; no asymptotics are contended.
    """
    forward: set[int] = set()
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex in forward:
            continue
        forward.add(vertex)
        for successor in adjacency[vertex]:
            if successor in active and successor not in forward:
                stack.append(successor)

    backward: set[int] = set()
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex in backward:
            continue
        backward.add(vertex)
        for predecessor in active:
            if predecessor not in backward and vertex in adjacency[predecessor]:
                stack.append(predecessor)
    return forward & backward


def _johnson_circuits(
    adjacency: list[list[int]], names: tuple[str, ...]
) -> tuple[tuple[str, ...], ...]:
    """Enumerate every elementary circuit of ``adjacency`` exactly once.

    Johnson's (1975) algorithm: for each vertex ``start`` in increasing index
    order, restrict to the subgraph induced by ``start..n-1`` and to ``start``'s
    strongly connected component within it, then run the blocked DFS that
    reports every circuit whose least vertex is ``start``. Each circuit is thus
    found exactly once, in a canonical orientation starting at its least
    vertex. Returns the circuits as tuples of the node names from ``names``.

    Determinism: vertices are ordered by ``names`` (the sorted casino list), and
    adjacency successor lists are sorted, so traversal order is fixed.
    """
    circuit_count = len(adjacency)
    circuits: list[tuple[str, ...]] = []

    for start in range(circuit_count):
        active = set(range(start, circuit_count))
        component = _strongly_connected_component_starting_at(adjacency, active, start)
        # `component` always contains `start` itself (it is reachable to and
        # from itself trivially), so there is no empty-component branch to guard.
        _solve_start(adjacency, component, start, names, circuits)

    return tuple(circuits)


def _solve_start(
    adjacency: list[list[int]],
    component: set[int],
    start: int,
    names: tuple[str, ...],
    circuits: list[tuple[str, ...]],
) -> None:
    """Run Johnson's blocked search for one least vertex ``start``.

    ``component`` is ``start``'s strongly connected component in the subgraph
    induced by ``start..n-1``. The closures below capture only the parameters
    of this function (never a loop variable), so each invocation owns its own
    ``blocked`` / ``banned`` / ``stack`` state.
    """
    blocked: dict[int, bool] = {vertex: False for vertex in component}
    banned: dict[int, set[int]] = {vertex: set() for vertex in component}
    stack: list[int] = []

    def unblock(vertex: int) -> None:
        blocked[vertex] = False
        for successor in list(banned[vertex]):
            banned[vertex].discard(successor)
            if blocked[successor]:
                unblock(successor)

    def circuit(vertex: int) -> bool:
        found_any = False
        stack.append(vertex)
        blocked[vertex] = True
        for successor in adjacency[vertex]:
            if successor not in component:
                continue
            if successor == start:
                circuits.append(tuple(names[i] for i in stack) + (names[start],))
                found_any = True
            elif not blocked[successor]:
                if circuit(successor):
                    found_any = True
        if found_any:
            unblock(vertex)
        else:
            for successor in adjacency[vertex]:
                if successor in component:
                    banned[successor].add(vertex)
        stack.pop()
        return found_any

    circuit(start)


def compute_hub(network: CasinoNetwork) -> str:
    """Module-level hub helper (gadget-friendly wrapper around :meth:`CasinoNetwork.hub`)."""
    return network.hub()


def laundering_closure(network: CasinoNetwork) -> float:
    """Module-level closure helper (gadget-friendly wrapper)."""
    return network.laundering_closure()


def canonical_network() -> CasinoNetwork:
    """The canonical CONFLICT STONE Las Vegas network.

    Casino proceeds from the Whyte operation are pushed through the strip as
    overlapping circular transfers so a fraction of the money visibly cycles
    (the laundering signal) while the rest passes through to the fence.
    """
    network = CasinoNetwork()
    # Two-node laundering loop on the strip.
    network.add_transfer("whyte_house", "stardust", 5.0)
    network.add_transfer("stardust", "dunes", 5.0)
    network.add_transfer("dunes", "stardust", 3.0)
    # Three-node circular wash.
    network.add_transfer("whyte_house", "sahara", 4.0)
    network.add_transfer("sahara", "tropicana", 4.0)
    network.add_transfer("tropicana", "whyte_house", 4.0)
    # Second two-node loop.
    network.add_transfer("whyte_house", "caesars", 2.0)
    network.add_transfer("caesars", "sands", 2.0)
    network.add_transfer("sands", "caesars", 2.0)
    return network
