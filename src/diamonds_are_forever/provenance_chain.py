"""Conflict-diamond provenance chain: custody graph, break points.

CONFLICT STONE models the paper trail of smuggled diamonds from mine to market
as an ordered chain of custody. A *break point* is a handoff whose provenance
cannot be verified — the classic forensic marker of conflict / illicit goods.

A chain is an ordered sequence of :class:`CustodyTransfer` handoffs. Legitimate
governance demands the chain be:

* **continuous** — each handoff's ``target`` equals the next handoff's
  ``source`` (no missing link);
* **acyclic** — a gem never returns to an actor it already left (a cycle is a
  laundering loop, not a provenance path);
* **documented** — every handoff with ``recorded=False`` is a visible hole.

This module is pure Python (stdlib ``math`` only where needed) so it stays
importable without BOND-API.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

__all__ = [
    "ChainInconsistencyError",
    "CustodyTransfer",
    "break_points",
    "build_chain",
    "canonical_transfers",
    "is_conflict_free",
    "provenance_coverage",
    "trace_origin",
    "validate_transfers",
]


class ChainInconsistencyError(ValueError):
    """Raised when a custody chain is not a continuous, acyclic path."""


@dataclass(frozen=True)
class CustodyTransfer:
    """One handoff of a gem from ``source`` to ``target``.

    ``recorded`` marks whether the transfer carries verifiable documentation.
    ``False`` means this step is a provenance break point.
    """

    source: str
    target: str
    recorded: bool
    gem: str = "conflict-diamond-lot"
    note: str = ""

    def __post_init__(self) -> None:
        for label, value in (
            ("source", self.source),
            ("target", self.target),
            ("gem", self.gem),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"CustodyTransfer.{label} must be a non-empty string")
        if not isinstance(self.recorded, bool):
            raise TypeError("CustodyTransfer.recorded must be a bool")


def validate_transfers(
    transfers: list[CustodyTransfer] | tuple[CustodyTransfer, ...],
) -> tuple[CustodyTransfer, ...]:
    """Validate a custody sequence and return it as an immutable tuple."""
    if not isinstance(transfers, (list, tuple)):
        raise TypeError("transfers must be a sequence of CustodyTransfer")
    for transfer in transfers:
        if not isinstance(transfer, CustodyTransfer):
            raise TypeError("transfers entries must be CustodyTransfer instances")
    return tuple(transfers)


def build_chain(
    transfers: list[CustodyTransfer] | tuple[CustodyTransfer, ...],
) -> tuple[CustodyTransfer, ...]:
    """Return the validated chain, enforcing continuity and acyclicity.

    Raises:
        ChainInconsistencyError: if the chain is empty, a transfer moves a gem
            to the same actor, consecutive transfers are discontinuous, or an
            actor is revisited (cycle).
    """
    validated = validate_transfers(transfers)
    if not validated:
        raise ChainInconsistencyError("custody chain must contain at least one transfer")
    if validated[0].source == validated[0].target:
        raise ChainInconsistencyError(
            f"a custody transfer cannot move a gem to the same actor: {validated[0].target!r}"
        )
    for previous, current in pairwise(validated):
        if previous.target != current.source:
            raise ChainInconsistencyError(
                f"chain discontinuity: {previous.target!r} hands off to {current.source!r}"
            )
    seen: set[str] = set()
    for actor in (validated[0].source, *(transfer.target for transfer in validated)):
        if actor in seen:
            raise ChainInconsistencyError(
                f"chain revisits actor {actor!r} — a laundering loop, not a custody path"
            )
        seen.add(actor)
    return validated


def break_points(
    transfers: list[CustodyTransfer] | tuple[CustodyTransfer, ...],
) -> tuple[int, ...]:
    """Return the 0-based indices of undocumented (break-point) handoffs."""
    validated = validate_transfers(transfers)
    return tuple(index for index, transfer in enumerate(validated) if not transfer.recorded)


def provenance_coverage(
    transfers: list[CustodyTransfer] | tuple[CustodyTransfer, ...],
) -> float:
    """Return the fraction of documented handoffs (0.0 when the chain is empty)."""
    validated = validate_transfers(transfers)
    if not validated:
        return 0.0
    recorded = sum(1 for transfer in validated if transfer.recorded)
    return recorded / len(validated)


def is_conflict_free(
    transfers: list[CustodyTransfer] | tuple[CustodyTransfer, ...],
) -> bool:
    """True when every handoff is documented (no break point)."""
    return not break_points(transfers)


def trace_origin(
    transfers: list[CustodyTransfer] | tuple[CustodyTransfer, ...],
    node: str,
) -> tuple[str, ...]:
    """Return the ordered actor path from the chain's origin to ``node``.

    The returned tuple starts at the origin (the first ``source``) and ends at
    ``node`` inclusive. Tracing the origin to itself is the single-element path
    ``(origin,)``: the origin is never any handoff's ``target`` in an acyclic
    chain, so without an explicit early return the scan would fall off the end
    and hand back the entire chain.

    Raises:
        ValueError: if ``node`` is empty.
        ChainInconsistencyError: if the chain is empty or ``node`` is absent.
    """
    validated = validate_transfers(transfers)
    if not isinstance(node, str) or not node.strip():
        raise ValueError("node must be a non-empty string")
    if not validated:
        raise ChainInconsistencyError("cannot trace origin of an empty chain")
    origin = validated[0].source
    if node == origin:
        return (origin,)
    targets = [transfer.target for transfer in validated]
    if node not in targets:
        raise ChainInconsistencyError(f"node {node!r} is not part of the custody chain")
    # Slice to the first arrival at `node` rather than scanning with a break:
    # after the origin case is handled, `node` is guaranteed to be a target, so
    # a break-loop would carry a fall-through arm that can never be reached.
    return (origin, *targets[: targets.index(node) + 1])


def canonical_transfers() -> tuple[CustodyTransfer, ...]:
    """The canonical CONFLICT STONE custody route.

    Tracks a diamond lot mined in Sierra Leone, smuggled via Nairobi to London,
    handed to Bond's cover (the dealer), then carried to Las Vegas. The two
    smuggling hops (mine -> broker, broker -> Nairobi) are undocumented —
    the provenance break points that mark the lot as conflict goods.
    """
    return (
        CustodyTransfer(
            "sierra_leone_mine",
            "illicit_broker",
            recorded=False,
            note="mined without certification",
        ),
        CustodyTransfer(
            "illicit_broker", "nairobi_courier", recorded=False, note="wildcat smuggling leg"
        ),
        CustodyTransfer(
            "nairobi_courier",
            "london_dealer",
            recorded=True,
            note="cover consignment, doctored papers",
        ),
        CustodyTransfer(
            "london_dealer", "amsterdam_contact", recorded=True, note="Tiffany Case handoff"
        ),
        CustodyTransfer(
            "amsterdam_contact",
            "las_vegas_fence",
            recorded=True,
            note="delivery to Whyte operation",
        ),
    )
