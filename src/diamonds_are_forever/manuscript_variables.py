"""Manuscript variable hydration for CONFLICT STONE.

Every ``{{TOKEN}}`` in ``manuscript/NN_*.md`` resolves through
:func:`generate_variables`, which reads ``manuscript/config.yaml`` plus the
computed analytic metrics from the pure domain modules. Metrics are never
hand-authored in prose — they flow through this module so the manuscript cannot
drift from the code it describes.

The consuming orchestrator is ``scripts/z_generate_manuscript_variables.py``; the
live cross-reference gate lives in ``tests/test_manuscript_variables.py``.
"""

from __future__ import annotations

import platform
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from diamonds_are_forever import (
    beam_physics,
    benford_audit,
    casino_network,
    lot_forensics,
    orbital_mirror,
    provenance_chain,
    smuggling_routes,
)

__all__ = ["generate_variables", "load_manuscript_config", "resolve_manuscript_tree"]

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "manuscript" / "config.yaml"

_TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def load_manuscript_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate ``manuscript/config.yaml`` (or an explicit path)."""
    path = Path(config_path) if config_path is not None else DEFAULT_CONFIG_PATH
    if not path.is_file():
        raise FileNotFoundError(f"manuscript config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"manuscript config must be a top-level mapping, got {type(data).__name__}")
    return data


def generate_variables(
    *,
    config_path: str | Path | None = None,
) -> dict[str, str]:
    """Compute the ``{{TOKEN}}`` -> value mapping for the CONFLICT STONE manuscript.

    Args:
        config_path: Override for ``manuscript/config.yaml``.

    The analytic tokens are computed live from the frozen canonical datasets in
    the pure domain core, so the manuscript cannot drift from the code.
    """
    config = load_manuscript_config(config_path)
    paper = config.get("paper", {})
    if not isinstance(paper, dict):
        raise TypeError("manuscript config 'paper' section must be a mapping")

    transfers = provenance_chain.canonical_transfers()
    coverage = provenance_chain.provenance_coverage(transfers)

    corridors = smuggling_routes.canonical_corridors()
    cargo_value = smuggling_routes.canonical_cargo_value_m()
    route, route_cost, survival = smuggling_routes.least_risk_route(
        corridors, "sierra_leone", "las_vegas", cargo_value
    )
    naive_route = smuggling_routes.naive_hops_route(corridors, "sierra_leone", "las_vegas")
    naive_cost = smuggling_routes.cost_of_path(corridors, naive_route, cargo_value)

    forensic = lot_forensics.audit_lot(lot_forensics.canonical_lot_samples())

    network = casino_network.canonical_network()
    closure = network.laundering_closure()

    ledger = benford_audit.benford_report(benford_audit.canonical_ledger_amounts())
    legitimate_ledger = benford_audit.benford_report(benford_audit.legitimate_ledger_amounts())
    laundered_deposits = benford_audit.laundered_deposit_amounts()
    ledger_contributions = benford_audit.digit_contributions(
        {int(digit): count for digit, count in ledger.distribution.items()}
    )
    carrier_digit = max(ledger_contributions, key=lambda digit: ledger_contributions[digit])
    carrier_share = ledger_contributions[carrier_digit] / sum(ledger_contributions.values())

    satellite = orbital_mirror.canonical_satellite()
    targets = orbital_mirror.canonical_targets()
    visible = [t.name for t in targets if orbital_mirror.is_visible(satellite, t)]

    beam = beam_physics.beam_metrics()
    scenario = beam_physics.canonical_beam_scenario()
    transmittance = beam_physics.atmospheric_transmittance(
        scenario.attenuation_per_km, scenario.atmosphere_path_km
    )
    occulted = [t.name for t in targets if not orbital_mirror.is_visible(satellite, t)]

    mission = config.get("mission", {})
    if not isinstance(mission, dict):
        raise TypeError("manuscript config 'mission' section must be a mapping")

    return {
        "CONFLICT_IDENTITY": str(mission.get("film", "")),
        "CONFLICT_CODENAME": str(mission.get("codename", "")),
        "CONFLICT_TITLE": str(paper.get("title", "")),
        "CONFLICT_SUBTITLE": str(paper.get("subtitle", "")),
        "CONFLICT_VERSION": str(paper.get("version", "")),
        "CONFLICT_KEYWORDS": ", ".join(str(k) for k in config.get("keywords", [])),
        "PROVENANCE_TRANSFERS": str(len(transfers)),
        "PROVENANCE_BREAKPOINTS": str(len(provenance_chain.break_points(transfers))),
        "PROVENANCE_COVERAGE_PCT": f"{coverage:.0%}",
        "PROVENANCE_CONFLICT_FREE": str(provenance_chain.is_conflict_free(transfers)).lower(),
        "SMUGGLE_CORRIDORS": str(len(corridors.corridors())),
        "SMUGGLE_ROUTE": " -> ".join(route),
        "SMUGGLE_NAIVE_ROUTE": " -> ".join(naive_route),
        "SMUGGLE_CARGO_VALUE_M": f"{cargo_value:.1f}",
        "SMUGGLE_EXPECTED_COST_M": f"{route_cost:.2f}",
        "SMUGGLE_NAIVE_COST_M": f"{naive_cost:.2f}",
        "SMUGGLE_SURVIVAL_PCT": f"{survival:.0%}",
        "SMUGGLE_EXPOSURE_PCT": f"{smuggling_routes.route_exposure(survival):.0%}",
        "SMUGGLE_REDUCTION_PCT": f"{smuggling_routes.route_reduction(naive_cost, route_cost):.0%}",
        "LOT_ID": lot_forensics.CANONICAL_LOT_ID,
        "LOT_SAMPLES": str(len(forensic.samples)),
        "LOT_ANOMALIES": str(len(forensic.anomalies)),
        "LOT_AUDIT_SCORE": str(forensic.score),
        "LOT_VERDICT": forensic.verdict,
        "LOT_CUTTING_ALLOWANCE_PCT": f"{lot_forensics.CUTTING_LOSS_LIMIT:.0%}",
        "LOT_DENSITY_NOMINAL": f"{lot_forensics.DIAMOND_DENSITY_G_CM3:.2f}",
        "LOT_DENSITY_MIN": f"{lot_forensics.DENSITY_MIN_G_CM3:.2f}",
        "LOT_DENSITY_MAX": f"{lot_forensics.DENSITY_MAX_G_CM3:.2f}",
        "CASINO_CASINOS": str(len(network.casinos())),
        "CASINO_TRANSFERS": str(len(network.transfers())),
        "CASINO_TOTAL_FLOW_M": f"{network.total_flow():.1f}",
        "CASINO_HUB": network.hub(),
        "CASINO_MONEY_CYCLES": str(len(network.find_money_cycles())),
        "CASINO_LAUNDERING_CLOSURE_PCT": f"{closure:.0%}",
        "BENFORD_TRANSACTIONS": str(ledger.transactions),
        "BENFORD_CHI_SQUARE": f"{ledger.chi_square:.2f}",
        "BENFORD_CRITICAL_VALUE": f"{ledger.critical_value:.3f}",
        "BENFORD_ALPHA": f"{benford_audit.BENFORD_ALPHA:g}",
        "BENFORD_DF": str(benford_audit.BENFORD_DEGREES_OF_FREEDOM),
        "BENFORD_VERDICT": "conforms" if ledger.conforms else "anomalous",
        "BENFORD_LEGIT_TRANSACTIONS": str(legitimate_ledger.transactions),
        "BENFORD_LEGIT_CHI_SQUARE": f"{legitimate_ledger.chi_square:.2f}",
        "BENFORD_LEGIT_VERDICT": "conforms" if legitimate_ledger.conforms else "anomalous",
        "BENFORD_LAUNDERED_TRANSACTIONS": str(len(laundered_deposits)),
        "BENFORD_CARRIER_DIGIT": str(carrier_digit),
        "BENFORD_CARRIER_SHARE_PCT": f"{carrier_share:.0%}",
        "ORBITAL_ALTITUDE_KM": f"{satellite.altitude_km:.0f}",
        "ORBITAL_TARGETS": str(len(targets)),
        "ORBITAL_VISIBLE_TARGETS": str(len(visible)),
        "ORBITAL_VISIBLE_NAMES": ", ".join(visible),
        "ORBITAL_OCCULTED_NAMES": ", ".join(occulted),
        "BEAM_MIRROR_DIAMETER_M": f"{scenario.mirror_diameter_m:.0f}",
        "BEAM_WAVELENGTH_NM": f"{scenario.wavelength_m * 1.0e9:.0f}",
        "BEAM_SLANT_RANGE_KM": f"{scenario.slant_range_km:,.0f}",
        "BEAM_TRANSMITTANCE_PCT": f"{transmittance:.0%}",
        "BEAM_SPOT_RADIUS_M": f"{beam['spot_radius_m']:.2f}",
        "BEAM_IRRADIANCE_W_M2": f"{beam['irradiance_w_m2']:,.0f}",
        "BEAM_CONCENTRATION_X": f"{beam['concentration']:.0f}",
        "BEAM_VAPORIZE_TIME_S": f"{beam['vaporize_time_s']:.0f}",
        "BEAM_REQUIRED_IRRADIANCE_MW": (
            f"{beam_physics.REQUIRED_STRIKE_IRRADIANCE_W_M2 / 1.0e6:g}"
        ),
        "BEAM_MIN_MIRROR_DIAMETER_M": f"{beam['min_mirror_diameter_m']:.1f}",
        "PYTHON_VERSION": platform.python_version(),
        "GENERATION_TIMESTAMP": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def resolve_manuscript_tree(
    variables: dict[str, str],
    *,
    manuscript_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    strict: bool = True,
) -> tuple[Path, list[str]]:
    """Copy each manuscript section to ``output/manuscript/``, substituting tokens.

    Only ``NN_*.md`` section files are copied (not sidecars such as SYNTAX.md).
    In strict mode any leftover ``{{TOKEN}}`` fails the resolution so the
    manuscript can never render with raw braces.

    Returns the output directory and the sorted list of resolved file names.
    """
    manuscript_dir = (
        Path(manuscript_dir) if manuscript_dir is not None else PACKAGE_ROOT / "manuscript"
    )
    output_dir = (
        Path(output_dir) if output_dir is not None else PACKAGE_ROOT / "output" / "manuscript"
    )
    resolved: list[str] = []
    for source in sorted(manuscript_dir.glob("[0-9][0-9]_*.md")):
        text = source.read_text(encoding="utf-8")
        for token, value in variables.items():
            text = text.replace("{{" + token + "}}", value)
        unresolved = sorted(set(_TOKEN_RE.findall(text)))
        if unresolved and strict:
            raise ValueError(f"unresolved manuscript tokens in {source.name}: {unresolved}")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / source.name).write_text(text, encoding="utf-8")
        resolved.append(source.name)
    if not resolved:
        raise FileNotFoundError(f"no numbered manuscript sections found in {manuscript_dir}")
    return output_dir, resolved
