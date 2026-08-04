"""Tests for CONFLICT STONE figure generation (deterministic, no mocks)."""

from __future__ import annotations

from pathlib import Path

from diamonds_are_forever.figures import (
    generate_all_figures,
    generate_casino_figure,
    generate_orbital_figure,
    generate_provenance_figure,
)


def _assert_png(path: Path) -> None:
    assert path.is_file()
    assert path.stat().st_size > 0
    assert path.read_bytes().startswith(b"\x89PNG")


def test_provenance_figure(tmp_path: Path) -> None:
    _assert_png(generate_provenance_figure(tmp_path / "provenance_chain.png"))


def test_casino_figure(tmp_path: Path) -> None:
    _assert_png(generate_casino_figure(tmp_path / "casino_network.png"))


def test_orbital_figure(tmp_path: Path) -> None:
    _assert_png(generate_orbital_figure(tmp_path / "orbital_visibility.png"))


def test_generate_all_figures(tmp_path: Path) -> None:
    provenance, casino, orbital = generate_all_figures(tmp_path / "figures")
    _assert_png(provenance)
    _assert_png(casino)
    _assert_png(orbital)
