"""Deterministic figure generation for CONFLICT STONE.

Each generator writes a PNG under ``output/figures/`` using ``matplotlib`` with
the non-interactive ``Agg`` backend. The figures are purely derived from the
pure-domain canonical datasets and are therefore byte-reproducible across runs.

Figures
-------
- ``provenance_chain.png`` — documented vs. break-point handoffs along the chain.
- ``casino_network.png`` — directed money-movement graph over the LV strip.
- ``orbital_visibility.png`` — slant-range / visibility summary per target.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt

from diamonds_are_forever import casino_network, orbital_mirror, provenance_chain

__all__ = [
    "generate_all_figures",
    "generate_casino_figure",
    "generate_orbital_figure",
    "generate_provenance_figure",
]


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
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=120)
    plt.close(figure)
    return path


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
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=120)
    plt.close(figure)
    return path


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
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=120)
    plt.close(figure)
    return path


def generate_all_figures(output_dir: str | Path) -> tuple[Path, Path, Path]:
    """Generate the three CONFLICT STONE figures under ``output_dir``."""
    output = Path(output_dir)
    return (
        generate_provenance_figure(output / "provenance_chain.png"),
        generate_casino_figure(output / "casino_network.png"),
        generate_orbital_figure(output / "orbital_visibility.png"),
    )
