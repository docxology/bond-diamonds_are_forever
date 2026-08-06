"""Tests for CONFLICT STONE figure generation (deterministic, no mocks).

Beyond "the PNG exists", the data-accessor tests bind each figure's plotted
series to the authoritative pure-core computation (V6), and the byte-identity
test proves the renders are reproducible.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from diamonds_are_forever import benford_audit, smuggling_routes
from diamonds_are_forever.figures import (
    benford_figure_data,
    cargo_sweep_figure_data,
    generate_all_figures,
    generate_beam_figure,
    generate_benford_figure,
    generate_cargo_sweep_figure,
    generate_casino_figure,
    generate_lot_figure,
    generate_orbital_figure,
    generate_provenance_figure,
    generate_smuggling_figure,
)

_ALL_FIGURE_NAMES = (
    "provenance_chain.png",
    "smuggling_route.png",
    "lot_forensics.png",
    "casino_network.png",
    "benford_ledger.png",
    "orbital_visibility.png",
    "beam_physics.png",
    "cargo_sweep.png",
)


def _assert_png(path: Path) -> None:
    assert path.is_file()
    assert path.stat().st_size > 0
    assert path.read_bytes().startswith(b"\x89PNG")


def test_provenance_figure(tmp_path: Path) -> None:
    _assert_png(generate_provenance_figure(tmp_path / "provenance_chain.png"))


def test_smuggling_figure(tmp_path: Path) -> None:
    _assert_png(generate_smuggling_figure(tmp_path / "smuggling_route.png"))


def test_lot_figure(tmp_path: Path) -> None:
    _assert_png(generate_lot_figure(tmp_path / "lot_forensics.png"))


def test_casino_figure(tmp_path: Path) -> None:
    _assert_png(generate_casino_figure(tmp_path / "casino_network.png"))


def test_benford_figure(tmp_path: Path) -> None:
    _assert_png(generate_benford_figure(tmp_path / "benford_ledger.png"))


def test_orbital_figure(tmp_path: Path) -> None:
    _assert_png(generate_orbital_figure(tmp_path / "orbital_visibility.png"))


def test_beam_figure(tmp_path: Path) -> None:
    _assert_png(generate_beam_figure(tmp_path / "beam_physics.png"))


def test_cargo_sweep_figure(tmp_path: Path) -> None:
    _assert_png(generate_cargo_sweep_figure(tmp_path / "cargo_sweep.png"))


def test_generate_all_figures(tmp_path: Path) -> None:
    paths = generate_all_figures(tmp_path / "figures")
    assert len(paths) == len(_ALL_FIGURE_NAMES)
    for path in paths:
        _assert_png(path)
    for name in _ALL_FIGURE_NAMES:
        assert (tmp_path / "figures" / name).is_file()


# ------------------------------------------------------------ content binding


def test_benford_figure_data_binds_to_the_ledger() -> None:
    """The Benford figure's bars equal what the core reports for the ledger."""
    data = benford_figure_data()
    assert data["digits"] == list(range(1, 10))
    assert data["control_conforms"] is True
    assert data["full_conforms"] is False
    assert len(data["control_freq"]) == len(data["observed"]) == len(data["expected"]) == 9
    # The figure's expected series is exactly Benford's law, no memory of any
    # dataset — a proxy that plotted the wrong expectation would fail here.
    for digit, expectation in zip(data["digits"], data["expected"]):
        assert expectation == pytest.approx(benford_audit.expected_benford_frequency(digit))


def test_cargo_sweep_figure_data_binds_to_the_router() -> None:
    """The sweep figure plots exactly what the router computes."""
    data = cargo_sweep_figure_data()
    values = data["cargo_values"]
    reductions = data["reductions"]
    assert values == list(smuggling_routes.canonical_cargo_sweep_values())
    sweep = smuggling_routes.cargo_reduction_sweep(values)
    assert [point.reduction for point in sweep] == pytest.approx(reductions)
    # The canonical cargo value is present and its reduction is the published one.
    canonical = smuggling_routes.canonical_cargo_value_m()
    assert canonical in values
    assert reductions[values.index(canonical)] == pytest.approx(0.1614, rel=1e-2)


# -------------------------------------------------------- reproducibility


def test_figures_are_byte_identical_across_two_renders(tmp_path: Path) -> None:
    """Two independent renders of all figures produce byte-identical PNGs (V6)."""
    first, second = tmp_path / "run1", tmp_path / "run2"
    generate_all_figures(first)
    generate_all_figures(second)
    for name in _ALL_FIGURE_NAMES:
        a = hashlib.sha256((first / name).read_bytes()).digest()
        b = hashlib.sha256((second / name).read_bytes()).digest()
        assert a == b, f"{name} is not byte-reproducible"
