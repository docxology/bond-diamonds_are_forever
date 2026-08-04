"""Tests for the CONFLICT STONE MissionProvider adapter (real protocol, no mocks)."""

from __future__ import annotations

from pathlib import Path

from bond_api.discovery import load_provider
from bond_api.protocol import (
    Debrief,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    ReconReport,
    ReconRequest,
    run_mission,
)
from bond_api.protocol import (
    MissionProvider as ProtocolCheck,
)
from bond_api.registry import GadgetRegistry

from diamonds_are_forever import casino_network
from diamonds_are_forever.mission import (
    CODENAME,
    MissionProvider,
    mission_input_hash,
    register_gadgets,
)

SRC = Path(__file__).resolve().parents[1] / "src"


def test_provider_satisfies_protocol() -> None:
    assert isinstance(MissionProvider(), ProtocolCheck)


def test_film_and_codename() -> None:
    provider = MissionProvider()
    assert provider.film == "diamonds_are_forever"
    assert CODENAME == "CONFLICT STONE"


def test_brief_shape() -> None:
    brief = MissionProvider().brief()
    assert isinstance(brief, MissionBrief)
    assert brief.codename == "CONFLICT STONE"
    assert len(brief.objectives) == 3
    assert len(brief.assets) == 3
    assert len(brief.constraints) == 2


def test_recon_reports_all_three_domains() -> None:
    report = MissionProvider().recon(ReconRequest(goal="survey"))
    assert isinstance(report, ReconReport)
    labels = {finding.label for finding in report.findings}
    assert {"chain", "casinos", "mirror", "goal"} <= labels


def test_plan_has_one_step_per_concept() -> None:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    assert isinstance(plan, MissionPlan)
    assert [step.action for step in plan.steps] == [
        "analyze_custody_chain",
        "analyze_money_movement",
        "solve_targeting_geometry",
    ]


def test_execute_results_match_canonical_math() -> None:
    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    assert isinstance(outcome, MissionOutcome)
    assert outcome.success is True
    provenance = outcome.results["provenance"]
    assert provenance == {
        "transfers": 5,
        "break_points": 2,
        "coverage": 0.6,
        "conflict_free": False,
    }
    assert outcome.results["casino"]["hub"] == "whyte_house"
    assert outcome.results["casino"]["money_cycles"] == 3
    assert outcome.results["orbital"]["visible_targets"] == 2


def test_debrief_is_deterministic() -> None:
    provider = MissionProvider()
    first = provider.debrief(provider.execute(provider.plan(provider.brief())))
    second = provider.debrief(provider.execute(provider.plan(provider.brief())))
    assert isinstance(first, Debrief)
    assert first.lessons == second.lessons
    assert first.outcome.provenance.input_hash == second.outcome.provenance.input_hash


def test_full_mission_flow() -> None:
    debrief = run_mission(MissionProvider(), ReconRequest(goal="execute the conflict-stone audit"))
    assert isinstance(debrief, Debrief)
    assert debrief.outcome.success is True
    assert debrief.outcome.provenance.seed == 7
    assert len(debrief.lessons) == 4


def test_input_hash_is_deterministic_and_nonempty() -> None:
    assert mission_input_hash() == mission_input_hash()
    assert len(mission_input_hash()) == 64


def test_gadget_registration() -> None:
    registry = GadgetRegistry()
    register_gadgets(registry)
    gadgets = registry.gadgets_for("diamonds_are_forever")
    assert gadgets == (
        "provenance.break_points",
        "provenance.coverage",
        "provenance.origin",
        "casino.hub",
        "casino.closure",
        "orbital.visible",
    )
    # Gadgets are real callables that return real results.
    hub_gadget = registry.lookup("diamonds_are_forever", "casino.hub")
    assert callable(hub_gadget)
    assert hub_gadget(casino_network.canonical_network()) == "whyte_house"


def test_discovery_loads_provider_by_slug() -> None:
    provider = load_provider("diamonds_are_forever", search_paths=[SRC])
    assert provider.film == "diamonds_are_forever"
    assert isinstance(provider, MissionProvider)


def test_outcome_round_trips_through_bond_serialization() -> None:
    from bond_api.serialization import from_json, to_json

    provider = MissionProvider()
    outcome = provider.execute(provider.plan(provider.brief()))
    text = to_json(outcome)
    decoded = from_json(text)
    assert decoded.results == outcome.results
    assert decoded.provenance.input_hash == outcome.provenance.input_hash
