"""Deterministic figure generation for CONFLICT STONE.

Each generator writes a PNG under ``output/figures/`` using ``matplotlib`` with
the non-interactive ``Agg`` backend. The figures are purely derived from the
pure-domain canonical datasets and are therefore byte-reproducible across runs.

Figures
-------
- ``provenance_chain.png`` — documented vs. break-point handoffs along the chain.
- ``smuggling_route.png`` — expected corridor costs with the optimum route marked.
- ``lot_forensics.png`` — per-handoff weight deltas vs. the cutting allowance.
- ``casino_network.png`` — directed money-movement graph over the LV strip.
- ``benford_ledger.png`` — observed vs. Benford-expected leading digits.
- ``orbital_visibility.png`` — slant-range / visibility summary per target.
- ``beam_physics.png`` — delivered irradiance vs. mirror diameter.
"""

from __future__ import annotations

import os
from itertools import pairwise
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from diamonds_are_forever import (
    beam_physics,
    benford_audit,
    casino_network,
    lot_forensics,
    orbital_mirror,
    provenance_chain,
    smuggling_routes,
)

__all__ = [
    "generate_all_figures",
    "generate_beam_figure",
    "generate_benford_figure",
    "generate_casino_figure",
    "generate_lot_figure",
    "generate_orbital_figure",
    "generate_provenance_figure",
    "generate_smuggling_figure",
]


def _save(figure: Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=120)
    plt.close(figure)
    return path


def generate_provenance_figure(output_path: str | Path) -> Path:
    """Bar chart of documented vs. break-point handoffs along the custody chain."""
    transfers = provenance_chain.canonical_transfers()
    names = [f"{t.source}->{t.target}" for t in transfers]
    recorded = [1 if t.recorded else 0 for t in transfers]
    figure, axis = plt.subplots(figsize=(8, 4))
    axis.bar(range(len(names)), recorded, color="#0f766e")
    axis.set_xticks(range(len(names)))
    axis.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    axis.set_ylim(0, 1.2)
    axis.set_ylabel("documented")
    axis.set_title("CONFLICT STONE — provenance chain break points")
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_smuggling_figure(output_path: str | Path) -> Path:
    """Bar chart of expected corridor costs with the optimal route highlighted."""
    network = smuggling_routes.canonical_corridors()
    cargo = smuggling_routes.canonical_cargo_value_m()
    route, _cost, _survival = smuggling_routes.least_risk_route(
        network, "sierra_leone", "las_vegas", cargo
    )
    route_edges = set(pairwise(route))
    corridors = network.corridors()
    labels = [f"{c.source}->{c.target}" for c in corridors]
    costs = [smuggling_routes.expected_cost(c, cargo) for c in corridors]
    colors = ["#b91c1c" if (c.source, c.target) in route_edges else "#cbd5e1" for c in corridors]
    figure, axis = plt.subplots(figsize=(9, 4))
    axis.bar(range(len(labels)), costs, color=colors)
    axis.set_xticks(range(len(labels)))
    axis.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    axis.set_ylabel("expected cost (M USD)")
    axis.set_title("CONFLICT STONE — smuggling corridor expected costs (red = optimum route)")
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_lot_figure(output_path: str | Path) -> Path:
    """Per-handoff weight deltas for lot DF-71 vs. the cutting allowance band."""
    samples = lot_forensics.canonical_lot_samples()
    report = lot_forensics.audit_lot(samples)
    labels = [f"{s.from_actor}->{s.to_actor}" for s in samples]
    deltas = list(report.deltas_g)
    allowances = [s.weight_in_g * lot_forensics.CUTTING_LOSS_LIMIT for s in samples]
    figure, axis = plt.subplots(figsize=(9, 4))
    axis.bar(range(len(labels)), deltas, color="#0f766e")
    axis.plot(
        range(len(labels)), allowances, color="#b91c1c", linestyle="--", label="cutting allowance"
    )
    axis.axhline(0.0, color="#334155", linewidth=1)
    axis.set_xticks(range(len(labels)))
    axis.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    axis.set_ylabel("weight delta (g)")
    axis.set_title("CONFLICT STONE — lot DF-71 weight reconciliation")
    axis.legend(loc="best")
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_casino_figure(output_path: str | Path) -> Path:
    """Directed money-movement graph over the canonical casino network."""
    network = casino_network.canonical_network()
    nodes = network.casinos()
    positions = {node: (index, 0.0) for index, node in enumerate(nodes)}
    figure, axis = plt.subplots(figsize=(8, 4))
    for node, (x, y) in positions.items():
        axis.plot(x, y, "o", color="#334155", markersize=14)
        axis.text(x, y - 0.12, node, ha="center", va="top", fontsize=8)
    for source, target, amount in network.transfers():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        axis.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops={"arrowstyle": "->", "color": "#b91c1c", "lw": 1.0 + amount},
        )
    axis.set_ylim(-0.6, 0.6)
    axis.axis("off")
    axis.set_title("CONFLICT STONE — casino money movement (line width ~ amount)")
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_benford_figure(output_path: str | Path) -> Path:
    """The matched control pair against the Benford expectation.

    Three bars per digit: the legitimate baseline (negative control), the full
    ledger, and the Benford expectation. Plotting the control alongside the
    flagged ledger is what makes the flag readable — the baseline tracks the
    expectation, the full ledger does not.
    """
    full = benford_audit.benford_report(benford_audit.canonical_ledger_amounts())
    control = benford_audit.benford_report(benford_audit.legitimate_ledger_amounts())
    digits = list(range(1, 10))
    control_freq = [float(control.distribution[str(d)]) / control.transactions for d in digits]
    observed = [float(full.distribution[str(d)]) / full.transactions for d in digits]
    expected = [benford_audit.expected_benford_frequency(d) for d in digits]
    figure, axis = plt.subplots(figsize=(8, 4))
    axis.bar(
        [d - 0.27 for d in digits],
        control_freq,
        width=0.27,
        color="#0369a1",
        label=f"legitimate baseline (chi2={control.chi_square:.2f}, conforms)",
    )
    axis.bar(
        digits,
        observed,
        width=0.27,
        color="#0f766e",
        label=f"full ledger (chi2={full.chi_square:.2f}, anomalous)",
    )
    axis.bar([d + 0.27 for d in digits], expected, width=0.27, color="#b91c1c", label="Benford")
    axis.set_xticks(digits)
    axis.set_xlabel("leading digit")
    axis.set_ylabel("frequency")
    axis.set_title("CONFLICT STONE — casino ledger vs. Benford's law")
    axis.legend(loc="best", fontsize=8)
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_orbital_figure(output_path: str | Path) -> Path:
    """Slant-range (km) bar chart per target, shaded by beam visibility."""
    satellite = orbital_mirror.canonical_satellite()
    targets = orbital_mirror.canonical_targets()
    names = [t.name for t in targets]
    ranges = [orbital_mirror.slant_range_km(satellite, t) for t in targets]
    visible = [orbital_mirror.is_visible(satellite, t) for t in targets]
    colors = ["#0f766e" if v else "#b91c1c" for v in visible]
    figure, axis = plt.subplots(figsize=(8, 4))
    axis.bar(range(len(names)), ranges, color=colors)
    axis.set_xticks(range(len(names)))
    axis.set_xticklabels(names, rotation=45, ha="right", fontsize=9)
    axis.set_ylabel("slant range (km)")
    axis.set_title("CONFLICT STONE — orbital-mirror targeting (green = in beam)")
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_beam_figure(output_path: str | Path) -> Path:
    """Delivered irradiance vs. mirror diameter with the canonical scenario marked."""
    scenario = beam_physics.canonical_beam_scenario()
    slant_range_m = scenario.slant_range_km * 1000.0
    diameters = list(range(10, 61, 2))
    irradiances = [
        beam_physics.delivered_irradiance_w_m2(
            d,
            scenario.wavelength_m,
            slant_range_m,
            scenario.attenuation_per_km,
            scenario.atmosphere_path_km,
        )
        for d in diameters
    ]
    minimum = beam_physics.minimum_mirror_diameter_m(
        scenario.wavelength_m,
        slant_range_m,
        beam_physics.REQUIRED_STRIKE_IRRADIANCE_W_M2,
        scenario.attenuation_per_km,
        scenario.atmosphere_path_km,
    )
    figure, axis = plt.subplots(figsize=(8, 4))
    axis.plot(diameters, irradiances, color="#0f766e")
    axis.axhline(
        beam_physics.REQUIRED_STRIKE_IRRADIANCE_W_M2,
        color="#b91c1c",
        linestyle="--",
        label=f"{beam_physics.REQUIRED_STRIKE_IRRADIANCE_W_M2 / 1.0e6:g} MW/m2 strike requirement",
    )
    axis.axvline(minimum, color="#334155", linestyle=":", label=f"min diameter {minimum:.1f} m")
    axis.set_xlabel("mirror diameter (m)")
    axis.set_ylabel("delivered irradiance (W/m2)")
    axis.set_title("CONFLICT STONE — beam delivery vs. mirror size at GEO")
    axis.legend(loc="best")
    figure.tight_layout()
    return _save(figure, Path(output_path))


def generate_all_figures(output_dir: str | Path) -> tuple[Path, ...]:
    """Generate every CONFLICT STONE figure under ``output_dir``."""
    output = Path(output_dir)
    return (
        generate_provenance_figure(output / "provenance_chain.png"),
        generate_smuggling_figure(output / "smuggling_route.png"),
        generate_lot_figure(output / "lot_forensics.png"),
        generate_casino_figure(output / "casino_network.png"),
        generate_benford_figure(output / "benford_ledger.png"),
        generate_orbital_figure(output / "orbital_visibility.png"),
        generate_beam_figure(output / "beam_physics.png"),
    )
