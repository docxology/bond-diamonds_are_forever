"""CONFLICT STONE — the MissionProvider adapter for *Diamonds Are Forever*.

This thin module implements the frozen :class:`bond_api.protocol.MissionProvider`
contract for the film package. All analytic heavy lifting lives in the pure
domain modules (:mod:`~diamonds_are_forever.provenance_chain`,
:mod:`~diamonds_are_forever.casino_network`, :mod:`~diamonds_are_forever.orbital_mirror`);
this module only wires them to the protocol lifecycle and registers their core
functions as BOND gadgets.

The provider is deterministic: seed 7, zero wall-clock dependence, provenance
fingerprinted from the canonical inputs via SHA-256.
"""

from __future__ import annotations

import hashlib
import json

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from diamonds_are_forever import casino_network, orbital_mirror, provenance_chain

__all__ = ["CODENAME", "PACKAGE_VERSION", "MissionProvider", "register_gadgets"]

#: Package version this mission reports in provenance.
PACKAGE_VERSION = "0.1.0"
#: Mission codename (CONFLICT STONE).
CODENAME = "CONFLICT STONE"
#: Deterministic RNG seed (0 disables randomness; we have none anyway).
SEED = 7


def mission_input_hash() -> str:
    """SHA-256 fingerprint of the canonical mission inputs (deterministic)."""
    payload = {
        "transfers": [
            [transfer.source, transfer.target, transfer.recorded, transfer.gem]
            for transfer in provenance_chain.canonical_transfers()
        ],
        "network": [list(edge) for edge in casino_network.canonical_network().transfers()],
        "satellite": {
            "altitude_km": orbital_mirror.canonical_satellite().altitude_km,
            "lat_deg": orbital_mirror.canonical_satellite().lat_deg,
            "lon_deg": orbital_mirror.canonical_satellite().lon_deg,
        },
        "targets": [
            [target.name, target.lat_deg, target.lon_deg]
            for target in orbital_mirror.canonical_targets()
        ],
    }
    canonical = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def register_gadgets(registry: GadgetRegistry) -> None:
    """Register the film's analytic functions as BOND gadgets under this slug."""
    registry.register(
        "diamonds_are_forever",
        {
            "provenance.break_points": provenance_chain.break_points,
            "provenance.coverage": provenance_chain.provenance_coverage,
            "provenance.origin": provenance_chain.trace_origin,
            "casino.hub": casino_network.compute_hub,
            "casino.closure": casino_network.laundering_closure,
            "orbital.visible": orbital_mirror.is_visible,
        },
    )


class MissionProvider:
    """Deterministic MissionProvider for CONFLICT STONE.

    The lifecycle stages brief / recon / plan / execute / debrief each return
    the BOND protocol dataclass named in their annotation and run real
    analytics over the canonical datasets (no mocks, no RNG).
    """

    film = "diamonds_are_forever"

    def brief(self) -> MissionBrief:
        """Declare the three CONFLICT STONE objectives and their assets."""
        transfers = provenance_chain.canonical_transfers()
        network = casino_network.canonical_network()
        targets = orbital_mirror.canonical_targets()
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=(
                "trace the conflict-diamond custody chain and pinpoint provenance break points",
                "map Las Vegas casino money movement and measure laundering closure",
                "solve orbital-mirror targeting geometry and beam delivery",
            ),
            assets=(
                Asset(
                    kind="custody_chain",
                    name="conflict_stone_route",
                    payload={"transfers": len(transfers)},
                ),
                Asset(
                    kind="casino_network",
                    name="las_vegas_strip",
                    payload={
                        "casinos": len(network.casinos()),
                        "transfers": len(network.transfers()),
                    },
                ),
                Asset(
                    kind="satellite",
                    name="space_mirror",
                    payload={
                        "altitude_km": orbital_mirror.canonical_satellite().altitude_km,
                        "targets": len(targets),
                    },
                ),
            ),
            constraints=(
                Constraint(
                    kind="determinism", detail="fixed datasets, no random draws, no external calls"
                ),
                Constraint(kind="provenance", detail="outcomes carry a SHA-256 input fingerprint"),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the three domains and surface their measured state."""
        transfers = provenance_chain.canonical_transfers()
        network = casino_network.canonical_network()
        satellite = orbital_mirror.canonical_satellite()
        targets = orbital_mirror.canonical_targets()
        visible = [
            target.name for target in targets if orbital_mirror.is_visible(satellite, target)
        ]
        return ReconReport(
            findings=(
                Finding(
                    label="chain",
                    detail=(
                        f"{len(transfers)} handoffs, {len(provenance_chain.break_points(transfers))} "
                        "provenance break points"
                    ),
                ),
                Finding(
                    label="casinos",
                    detail=f"{len(network.casinos())} casinos, {len(network.transfers())} transfers",
                ),
                Finding(
                    label="mirror",
                    detail=f"{len(visible)} of {len(targets)} targets within visible face: {', '.join(visible)}",
                ),
                Finding(label="goal", detail=request.goal),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan one analytic step per concept, sized by the canonical datasets."""
        return MissionPlan(
            steps=(
                Step(
                    name="provenance",
                    action="analyze_custody_chain",
                    params={"objectives": len(brief.objectives)},
                ),
                Step(
                    name="casino",
                    action="analyze_money_movement",
                    params={"casinos": len(casino_network.canonical_network().casinos())},
                ),
                Step(
                    name="orbital",
                    action="solve_targeting_geometry",
                    params={"targets": len(orbital_mirror.canonical_targets())},
                ),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the three analyses and return a deterministic outcome with provenance."""
        transfers = provenance_chain.canonical_transfers()
        coverage = provenance_chain.provenance_coverage(transfers)
        break_count = len(provenance_chain.break_points(transfers))

        network = casino_network.canonical_network()
        cycles = network.find_money_cycles()
        closure = network.laundering_closure()

        satellite = orbital_mirror.canonical_satellite()
        targets = orbital_mirror.canonical_targets()
        visible = [
            target.name for target in targets if orbital_mirror.is_visible(satellite, target)
        ]
        ranges = {
            target.name: round(orbital_mirror.slant_range_km(satellite, target), 1)
            for target in targets
        }

        results = {
            "provenance": {
                "transfers": len(transfers),
                "break_points": break_count,
                "coverage": round(coverage, 4),
                "conflict_free": provenance_chain.is_conflict_free(transfers),
            },
            "casino": {
                "casinos": len(network.casinos()),
                "transfers": len(network.transfers()),
                "total_flow_m": round(network.total_flow(), 2),
                "hub": network.hub(),
                "money_cycles": len(cycles),
                "laundering_closure": round(closure, 4),
            },
            "orbital": {
                "altitude_km": int(satellite.altitude_km),
                "targets": len(targets),
                "visible_targets": len(visible),
                "visible_names": list(visible),
                "slant_ranges_km": ranges,
            },
            "steps_completed": len(plan.steps),
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=SEED,
                input_hash=mission_input_hash(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarise the mission outcome and record CONFLICT STONE's standing lessons."""
        results: dict = outcome.results
        provenance: dict = results["provenance"]
        casino: dict = results["casino"]
        orbital: dict = results["orbital"]
        return Debrief(
            outcome=outcome,
            lessons=(
                f"an undocumented handoff is a provenance break: coverage of {provenance['coverage']:.0%} still leaves flagrant conflict-goods exposure",
                f"circular money movement is the laundering signature: closure of {casino['laundering_closure']:.0%} over {casino['casinos']} casinos",
                f"an orbital mirror can only strike the visible face: {orbital['visible_targets']} of {orbital['targets']} targets in-beam",
                "the contract is frozen; films must not change it",
            ),
        )
