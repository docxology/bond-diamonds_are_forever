"""Las Vegas casino network analysis: inter-casino money movement.

CONFLICT STONE traces how diamond-smuggling proceeds are laundered through the
Las Vegas casino ecosystem. Money moves casino-to-casino along a directed,
weighted multigraph; analysis surfaces gross flow, net positions, circular
(laundering) paths, and the network's hub casino.

Everything is deterministic: amounts are exact ``float`` values accumulated in
insertion order, iteration follows insertion order, and there is no RNG.
"""

from __future__ import annotations

from collections import defaultdict
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
        return sum(amount for (_, target), amount in self._edges.items() if target == casino)

    def total_outflow(self, casino: str) -> float:
        """Total money flowing out of ``casino`` (0.0 for an unknown casino)."""
        return sum(amount for (source, _), amount in self._edges.items() if source == casino)

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
        """All distinct directed money cycles (laundering loops).

        A cycle is reported once as ``(n0, n1, ..., n0)``, the nodes visited in
        DFS discovery order at the point the back edge is found.
        """
        adjacency: dict[str, list[str]] = defaultdict(list)
        for source, target in self._edges:
            adjacency[source].append(target)
        nodes = self.casinos()
        state: dict[str, int] = {node: 0 for node in nodes}  # 0 unvisited, 1 in-stack, 2 done
        stack: list[str] = []
        cycles: list[tuple[str, ...]] = []
        discovered: list[tuple[str, ...]] = []

        def visit(node: str) -> None:
            state[node] = 1
            stack.append(node)
            for nxt in adjacency.get(node, ()):
                if state.get(nxt, 0) == 1:
                    start = stack.index(nxt)
                    cycle = tuple(stack[start:] + [nxt])
                    if cycle not in discovered:
                        discovered.append(cycle)
                        cycles.append(cycle)
                elif state.get(nxt, 0) == 0:
                    visit(nxt)
            stack.pop()
            state[node] = 2

        for node in nodes:
            if state[node] == 0:
                visit(node)
        return tuple(cycles)

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
