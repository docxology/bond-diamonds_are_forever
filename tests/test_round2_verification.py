"""Round-2 verification tests for CONFLICT STONE (deterministic, no mocks).

Closes the TODO verification backlog:

- V2 — the beam scenario's slant range is bound to the geometry it claims, so
  changing the satellite altitude or the Washington DC target cannot leave the
  beam scenario computing at a stale range.
- V3 — the package version is single-sourced: pyproject, ``__init__``, the
  mission provenance block, and the manuscript config must all agree.
- V4 — the manuscript token gate is now two-directional: no generated token may
  be orphaned (computed but cited nowhere), and no cited token may be missing.
- V5 — the seven pure modules import without ``bond_api``; ``mission`` is the
  only module that may fail.
- V7 — the ``experiment_plan.yaml`` ablation rows for lot forensics and the
  smuggling corridors are recomputed and asserted, not prose.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest
import tomllib
import yaml

from diamonds_are_forever import __version__ as pkg_version
from diamonds_are_forever import (
    beam_physics,
    lot_forensics,
    orbital_mirror,
    smuggling_routes,
)
from diamonds_are_forever import manuscript_variables as mv
from diamonds_are_forever.casino_network import CasinoNetwork
from diamonds_are_forever.mission import PACKAGE_VERSION
from diamonds_are_forever.smuggling_routes import Corridor

ROOT = Path(__file__).resolve().parents[1]

_TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


# ------------------------------------------------------------------ V2


def test_beam_slant_range_binds_to_the_geometry_it_claims() -> None:
    """The beam scenario's slant range must equal the orbital geometry's range.

    ``beam_physics.canonical_beam_scenario()`` hardcodes ``36_998.4`` km with a
    comment ``# mirror -> Washington DC at GEO``. That value must equal what
    ``orbital_mirror.slant_range_km`` actually produces for the canonical
    satellite and the Washington DC target, or the beam metrics (and the
    minimum-mirror headline) are being computed at a range the mission no
    longer uses.
    """
    scenario = beam_physics.canonical_beam_scenario()
    satellite = orbital_mirror.canonical_satellite()
    washington = next(
        target for target in orbital_mirror.canonical_targets() if target.name == "Washington DC"
    )
    geometric = orbital_mirror.slant_range_km(satellite, washington)
    assert scenario.slant_range_km == pytest.approx(geometric, abs=0.01)
    # The headline metric is computed at exactly this range, so the binding is
    # the one that matters.
    assert beam_physics.beam_metrics()["min_mirror_diameter_m"] > 0


# ------------------------------------------------------------------ V3


def _pyproject_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    return project["version"]


def test_package_version_is_single_sourced() -> None:
    """All four version declarations must agree.

    ``pyproject.toml``, ``src/.../__init__.py`` (``__version__``),
    ``mission.py`` (``PACKAGE_VERSION``, which enters the provenance block), and
    ``manuscript/config.yaml`` (which becomes ``{{CONFLICT_VERSION}}``) are
    independent today; a bump in one must fail here rather than drift silently.
    """
    config = yaml.safe_load((ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))
    paper_version = config["paper"]["version"]
    versions = {
        "pyproject": _pyproject_version(),
        "__init__": pkg_version,
        "mission.PACKAGE_VERSION": PACKAGE_VERSION,
        "manuscript config": paper_version,
    }
    assert len(set(versions.values())) == 1, versions


# ------------------------------------------------------------------ V4


def test_no_generated_ms_token_is_orphaned() -> None:
    """The token gate closes in both directions.

    ``test_manuscript_variables.py`` already asserts no manuscript section cites
    an unknown token. This closes the other half: a variable that is computed
    and exported but cited in no numbered section is an orphan and must fail.
    """
    variables = mv.generate_variables()
    used: set[str] = set()
    for source in sorted((ROOT / "manuscript").glob("[0-9][0-9]_*.md")):
        used |= set(_TOKEN_RE.findall(source.read_text(encoding="utf-8")))
    orphans = set(variables) - used
    assert not orphans, f"generated-but-uncited tokens: {sorted(orphans)}"
    # The forward direction, for completeness of the two-way guarantee.
    assert not (used - set(variables))


# ------------------------------------------------------------------ V5


def test_pure_core_imports_without_bond_api() -> None:
    """The seven pure modules import with ``bond_api`` unavailable.

    Spawn a subprocess that installs a ``sys.meta_path`` finder raising
    ``ImportError`` for any ``bond_api`` name, imports each pure module plus the
    manifest/figures modules, and asserts ``mission`` is the *only* module that
    fails. This guards the stated fallback ("pure core importable without
    BOND-API") against one stray top-level import.
    """
    code = (
        "import sys\n"
        "class _Block:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'bond_api' or name.startswith('bond_api.'):\n"
        "            raise ImportError('bond_api blocked')\n"
        "        return None\n"
        "sys.meta_path.insert(0, _Block())\n"
        "from diamonds_are_forever import (\n"
        "    provenance_chain, smuggling_routes, lot_forensics, casino_network,\n"
        "    benford_audit, orbital_mirror, beam_physics, manuscript_variables,\n"
        "    figures,\n"
        ")\n"
        "try:\n"
        "    import diamonds_are_forever.mission  # noqa: F401\n"
        "except ImportError:\n"
        "    print('mission-blocked')\n"
        "else:\n"
        "    raise SystemExit('mission should not import without bond_api')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "mission-blocked" in result.stdout


# ------------------------------------------------------------------ V7


def test_lot_forensics_density_ablation_leaves_only_excessive_loss() -> None:
    """``experiment_plan.yaml``: remove density probe -> only excessive loss.

    Widening the density window so every measured density is genuine must leave
    exactly the one excessive-loss anomaly (the final diversion) and the lot
    verdict must drop to ``suspicious``.
    """
    report = lot_forensics.audit_lot(
        lot_forensics.canonical_lot_samples(), density_min=2.0, density_max=4.0
    )
    assert [anomaly[1] for anomaly in report.anomalies] == ["excessive_loss"]
    assert report.verdict == "suspicious"


def test_smuggling_single_chain_ablation_collapses_reduction() -> None:
    """``experiment_plan.yaml``: single corridor chain -> reduction collapses to 0.

    With only one possible route there is nothing to optimise, so the
    expected-cost optimum equals the fewest-hops baseline and the reduction is
    exactly zero (never negative).
    """
    network = smuggling_routes.SmugglingNetwork()
    network.add_corridor(Corridor("a", "b", 1.0, 0.10))
    network.add_corridor(Corridor("b", "c", 1.0, 0.10))
    route, cost, _survival = smuggling_routes.least_risk_route(network, "a", "c", 5.0)
    naive = smuggling_routes.naive_hops_route(network, "a", "c")
    naive_cost = smuggling_routes.cost_of_path(network, naive, 5.0)
    assert route == naive
    assert smuggling_routes.route_reduction(naive_cost, cost) == pytest.approx(0.0)


def test_casino_closure_is_well_defined_overlapping_circuits() -> None:
    """Closure stays in [0, 1] even on graphs with overlapping circuits."""
    network = CasinoNetwork()
    network.add_transfer("w", "s", 5.0)
    network.add_transfer("s", "d", 5.0)
    network.add_transfer("d", "s", 3.0)
    closure = network.laundering_closure()
    assert 0.0 <= closure <= 1.0


# ------------------------------------------------------------------ E4


def test_cargo_reduction_sweep_is_non_negative_and_cargo_dependent() -> None:
    """The sweep stays in [0, 1] and the optimum *changes* with cargo value.

    ``experiment_plan.yaml`` claims a cargo-value sensitivity; the honest,
    measured properties are that the reduction is never negative and that the
    expected-cost optimum shifts corridor as cargo value crosses the point where
    seizure risk overtakes transport cost. The curve is deliberately *not*
    asserted monotone: measured (above) it falls and then rises as the optimum
    switches from the Paris leg to the New York leg.
    """
    points = smuggling_routes.cargo_reduction_sweep(smuggling_routes.canonical_cargo_sweep_values())
    assert points
    assert all(0.0 <= point.reduction <= 1.0 for point in points)
    assert all(point.cargo_value_m >= 0.0 for point in points)
    # Cargo-dependence: the optimum route differs between starved and rich
    # consignments, so the reduction is not a single cargo-independent constant.
    low_route = points[0].route
    high_route = points[-1].route
    assert low_route != high_route
    # The canonical point reproduces the published ratio exactly.
    canonical = next(p for p in points if p.cargo_value_m == 5.0)
    assert canonical.reduction == pytest.approx(0.1614, rel=1e-2)


def test_cargo_reduction_sweep_rejects_negative_cargo() -> None:
    with pytest.raises(ValueError):
        smuggling_routes.cargo_reduction_sweep([-1.0])
