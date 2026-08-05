"""CONFLICT STONE — the MissionProvider adapter for *Diamonds Are Forever*.

This thin module implements the frozen :class:`bond_api.protocol.MissionProvider`
contract for the film package. All analytic heavy lifting lives in the pure
domain modules (:mod:`~diamonds_are_forever.provenance_chain`,
:mod:`~diamonds_are_forever.smuggling_routes`,
:mod:`~diamonds_are_forever.lot_forensics`,
:mod:`~diamonds_are_forever.casino_network`,
:mod:`~diamonds_are_forever.benford_audit`,
:mod:`~diamonds_are_forever.orbital_mirror`,
:mod:`~diamonds_are_forever.beam_physics`); this module only wires them to the
protocol lifecycle and registers their core functions as BOND gadgets.

The provider is deterministic: seed 7, zero wall-clock dependence, provenance
fingerprinted from the canonical inputs via SHA-256. The public protocol shape
(film, brief/recon/plan/execute/debrief, register_gadgets) is frozen and must
not change; deepening happens inside the package.
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

from diamonds_are_forever import (
    beam_physics,
    benford_audit,
    casino_network,
    lot_forensics,
    orbital_mirror,
    provenance_chain,
    smuggling_routes,
)

__all__ = ["CODENAME", "PACKAGE_VERSION", "MissionProvider", "register_gadgets"]

#: Package version this mission reports in provenance.
PACKAGE_VERSION = "0.1.0"
#: Mission codename (CONFLICT STONE).
CODENAME = "CONFLICT STONE"
#: Deterministic RNG seed (0 disables randomness; we have none anyway).
SEED = 7
#: Strike requirement in MW/m^2, derived from the beam core (never restated).
_REQUIRED_STRIKE_MW = beam_physics.REQUIRED_STRIKE_IRRADIANCE_W_M2 / 1.0e6


def mission_input_hash() -> str:
    """SHA-256 fingerprint of the canonical mission inputs (deterministic)."""
    corridors = smuggling_routes.canonical_corridors()
    payload = {
        "transfers": [
            [transfer.source, transfer.target, transfer.recorded, transfer.gem]
            for transfer in provenance_chain.canonical_transfers()
        ],
        "network": [list(edge) for edge in casino_network.canonical_network().transfers()],
        "corridors": [
            [c.source, c.target, c.cost_m, c.seizure_probability] for c in corridors.corridors()
        ],
        "cargo_value_m": smuggling_routes.canonical_cargo_value_m(),
        "lot_samples": [
            [
                s.lot,
                s.from_actor,
                s.to_actor,
                s.weight_in_g,
                s.weight_out_g,
                s.measured_density_g_cm3,
            ]
            for s in lot_forensics.canonical_lot_samples()
        ],
        "satellite": {
            "altitude_km": orbital_mirror.canonical_satellite().altitude_km,
            "lat_deg": orbital_mirror.canonical_satellite().lat_deg,
            "lon_deg": orbital_mirror.canonical_satellite().lon_deg,
        },
        "targets": [
            [target.name, target.lat_deg, target.lon_deg]
            for target in orbital_mirror.canonical_targets()
        ],
        "beam_scenario": {
            "mirror_diameter_m": beam_physics.canonical_beam_scenario().mirror_diameter_m,
            "wavelength_m": beam_physics.canonical_beam_scenario().wavelength_m,
            "slant_range_km": beam_physics.canonical_beam_scenario().slant_range_km,
            "attenuation_per_km": beam_physics.canonical_beam_scenario().attenuation_per_km,
            "atmosphere_path_km": beam_physics.canonical_beam_scenario().atmosphere_path_km,
        },
        "ledger": list(benford_audit.canonical_ledger_amounts()),
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
            "smuggling.route": smuggling_routes.least_risk_route,
            "smuggling.reduction": smuggling_routes.route_reduction,
            "forensics.audit": lot_forensics.audit_lot,
            "casino.hub": casino_network.compute_hub,
            "casino.closure": casino_network.laundering_closure,
            "benford.report": benford_audit.benford_report,
            "orbital.visible": orbital_mirror.is_visible,
            "beam.metrics": beam_physics.beam_metrics,
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
        """Declare the CONFLICT STONE objectives and their assets."""
        transfers = provenance_chain.canonical_transfers()
        network = casino_network.canonical_network()
        corridors = smuggling_routes.canonical_corridors()
        targets = orbital_mirror.canonical_targets()
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=(
                "trace the conflict-diamond custody chain and pinpoint provenance break points",
                "optimize the smuggling corridor route under seizure risk",
                "audit the diamond lot for weight and density fraud",
                "map Las Vegas casino money movement and measure laundering closure",
                "test the casino ledger against Benford's law",
                "solve orbital-mirror targeting geometry and beam delivery",
            ),
            assets=(
                Asset(
                    kind="custody_chain",
                    name="conflict_stone_route",
                    payload={"transfers": len(transfers)},
                ),
                Asset(
                    kind="corridor_network",
                    name="smuggling_network",
                    payload={
                        "corridors": len(corridors.corridors()),
                        "cargo_value_m": smuggling_routes.canonical_cargo_value_m(),
                    },
                ),
                Asset(
                    kind="lot_samples",
                    name="lot_df71",
                    payload={"samples": len(lot_forensics.canonical_lot_samples())},
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
                    kind="ledger",
                    name="casino_ledger",
                    payload={"transactions": len(benford_audit.canonical_ledger_amounts())},
                ),
                Asset(
                    kind="satellite",
                    name="space_mirror",
                    payload={
                        "altitude_km": orbital_mirror.canonical_satellite().altitude_km,
                        "targets": len(targets),
                        "mirror_diameter_m": beam_physics.canonical_beam_scenario().mirror_diameter_m,
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
        """Survey the domains and surface their measured state."""
        transfers = provenance_chain.canonical_transfers()
        network = casino_network.canonical_network()
        corridors = smuggling_routes.canonical_corridors()
        report = lot_forensics.audit_lot(lot_forensics.canonical_lot_samples())
        ledger = benford_audit.benford_report(benford_audit.canonical_ledger_amounts())
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
                    label="corridors",
                    detail=f"{len(corridors.corridors())} corridors in the smuggling network",
                ),
                Finding(
                    label="lot_forensics",
                    detail=f"{len(report.anomalies)} lot anomalies, verdict {report.verdict}",
                ),
                Finding(
                    label="casinos",
                    detail=f"{len(network.casinos())} casinos, {len(network.transfers())} transfers",
                ),
                Finding(
                    label="ledger",
                    detail=(
                        f"chi-square {ledger.chi_square} vs critical {ledger.critical_value} — "
                        f"{'conforms' if ledger.conforms else 'anomalous'}"
                    ),
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
                    name="smuggling",
                    action="optimize_corridor_route",
                    params={"corridors": len(smuggling_routes.canonical_corridors().corridors())},
                ),
                Step(
                    name="forensics",
                    action="audit_lot_df71",
                    params={"samples": len(lot_forensics.canonical_lot_samples())},
                ),
                Step(
                    name="casino",
                    action="analyze_money_movement",
                    params={"casinos": len(casino_network.canonical_network().casinos())},
                ),
                Step(
                    name="benford",
                    action="test_ledger_digit_law",
                    params={"transactions": len(benford_audit.canonical_ledger_amounts())},
                ),
                Step(
                    name="orbital",
                    action="solve_targeting_geometry",
                    params={"targets": len(orbital_mirror.canonical_targets())},
                ),
                Step(
                    name="beam",
                    action="solve_beam_delivery",
                    params={
                        "mirror_diameter_m": beam_physics.canonical_beam_scenario().mirror_diameter_m
                    },
                ),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the analyses and return a deterministic outcome with provenance."""
        transfers = provenance_chain.canonical_transfers()
        coverage = provenance_chain.provenance_coverage(transfers)
        break_count = len(provenance_chain.break_points(transfers))

        corridors = smuggling_routes.canonical_corridors()
        cargo_value = smuggling_routes.canonical_cargo_value_m()
        route, route_cost, survival = smuggling_routes.least_risk_route(
            corridors, "sierra_leone", "las_vegas", cargo_value
        )
        naive_route = smuggling_routes.naive_hops_route(corridors, "sierra_leone", "las_vegas")
        naive_cost = smuggling_routes.cost_of_path(corridors, naive_route, cargo_value)

        forensic = lot_forensics.audit_lot(lot_forensics.canonical_lot_samples())

        network = casino_network.canonical_network()
        cycles = network.find_money_cycles()
        closure = network.laundering_closure()

        ledger = benford_audit.benford_report(benford_audit.canonical_ledger_amounts())

        satellite = orbital_mirror.canonical_satellite()
        targets = orbital_mirror.canonical_targets()
        visible = [
            target.name for target in targets if orbital_mirror.is_visible(satellite, target)
        ]
        ranges = {
            target.name: round(orbital_mirror.slant_range_km(satellite, target), 1)
            for target in targets
        }

        beam = beam_physics.beam_metrics()

        results = {
            "provenance": {
                "transfers": len(transfers),
                "break_points": break_count,
                "coverage": round(coverage, 4),
                "conflict_free": provenance_chain.is_conflict_free(transfers),
            },
            "smuggling": {
                "corridors": len(corridors.corridors()),
                "route": list(route),
                "expected_cost_m": round(route_cost, 4),
                "survival": round(survival, 4),
                "exposure": round(smuggling_routes.route_exposure(survival), 4),
                "reduction": round(smuggling_routes.route_reduction(naive_cost, route_cost), 4),
            },
            "lot_forensics": {
                "samples": len(forensic.samples),
                "anomalies": len(forensic.anomalies),
                "score": forensic.score,
                "verdict": forensic.verdict,
            },
            "casino": {
                "casinos": len(network.casinos()),
                "transfers": len(network.transfers()),
                "total_flow_m": round(network.total_flow(), 2),
                "hub": network.hub(),
                "money_cycles": len(cycles),
                "laundering_closure": round(closure, 4),
            },
            "benford": {
                "transactions": ledger.transactions,
                "chi_square": ledger.chi_square,
                "critical_value": ledger.critical_value,
                "conforms": ledger.conforms,
            },
            "orbital": {
                "altitude_km": int(satellite.altitude_km),
                "targets": len(targets),
                "visible_targets": len(visible),
                "visible_names": list(visible),
                "slant_ranges_km": ranges,
            },
            "beam": {
                "spot_radius_m": round(beam["spot_radius_m"], 4),
                "irradiance_w_m2": round(beam["irradiance_w_m2"], 2),
                "concentration": round(beam["concentration"], 2),
                "vaporize_time_s": round(beam["vaporize_time_s"], 2),
                "min_mirror_diameter_m": round(beam["min_mirror_diameter_m"], 4),
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
        smuggling: dict = results["smuggling"]
        forensics: dict = results["lot_forensics"]
        casino: dict = results["casino"]
        benford: dict = results["benford"]
        orbital: dict = results["orbital"]
        beam: dict = results["beam"]
        return Debrief(
            outcome=outcome,
            lessons=(
                f"an undocumented handoff is a provenance break: coverage of {provenance['coverage']:.0%} still leaves flagrant conflict-goods exposure",
                f"seizure risk rewrites the route: the expected-cost optimum saves {smuggling['reduction']:.0%} over the fewest-hops baseline",
                f"weight and density tell the physical story: {forensics['anomalies']} lot anomalies, verdict {forensics['verdict']}",
                f"circular money movement is the laundering signature: closure of {casino['laundering_closure']:.0%} over {casino['casinos']} casinos",
                f"the ledger fails Benford's law: chi-square {benford['chi_square']} against a {benford['critical_value']} critical value",
                (
                    f"beam physics bounds the fantasy: a {beam['min_mirror_diameter_m']:.1f} m "
                    f"mirror delivers {_REQUIRED_STRIKE_MW:g} MW/m2 at geostationary range"
                ),
                f"an orbital mirror can only strike the visible face: {orbital['visible_targets']} of {orbital['targets']} targets in-beam",
                "the contract is frozen; films must not change it",
            ),
        )
