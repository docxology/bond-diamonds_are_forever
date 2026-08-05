"""Tests for CONFLICT STONE figure generation (deterministic, no mocks)."""

from __future__ import annotations

from pathlib import Path

from diamonds_are_forever.figures import (
    generate_all_figures,
    generate_beam_figure,
    generate_benford_figure,
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


def test_generate_all_figures(tmp_path: Path) -> None:
    paths = generate_all_figures(tmp_path / "figures")
    assert len(paths) == len(_ALL_FIGURE_NAMES)
    for path in paths:
        _assert_png(path)
    for name in _ALL_FIGURE_NAMES:
        assert (tmp_path / "figures" / name).is_file()
