"""Tests for manuscript variable hydration + the live {{TOKEN}} cross-reference gate."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from diamonds_are_forever import manuscript_variables as mv

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"

_TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def _write_config(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# ------------------------------------------------------------- generate_variables


def test_generate_variables_all_expected_keys() -> None:
    variables = mv.generate_variables()
    expected = {
        "CONFLICT_IDENTITY",
        "CONFLICT_CODENAME",
        "CONFLICT_TITLE",
        "CONFLICT_SUBTITLE",
        "CONFLICT_VERSION",
        "CONFLICT_KEYWORDS",
        "PROVENANCE_TRANSFERS",
        "PROVENANCE_BREAKPOINTS",
        "PROVENANCE_COVERAGE_PCT",
        "PROVENANCE_CONFLICT_FREE",
        "SMUGGLE_CORRIDORS",
        "SMUGGLE_ROUTE",
        "SMUGGLE_EXPECTED_COST_M",
        "SMUGGLE_SURVIVAL_PCT",
        "SMUGGLE_REDUCTION_PCT",
        "LOT_SAMPLES",
        "LOT_ANOMALIES",
        "LOT_AUDIT_SCORE",
        "LOT_VERDICT",
        "CASINO_CASINOS",
        "CASINO_TRANSFERS",
        "CASINO_TOTAL_FLOW_M",
        "CASINO_HUB",
        "CASINO_MONEY_CYCLES",
        "CASINO_LAUNDERING_CLOSURE_PCT",
        "BENFORD_TRANSACTIONS",
        "BENFORD_CHI_SQUARE",
        "BENFORD_VERDICT",
        "ORBITAL_ALTITUDE_KM",
        "ORBITAL_TARGETS",
        "ORBITAL_VISIBLE_TARGETS",
        "ORBITAL_VISIBLE_NAMES",
        "BEAM_SPOT_RADIUS_M",
        "BEAM_CONCENTRATION_X",
        "BEAM_VAPORIZE_TIME_S",
        "BEAM_MIN_MIRROR_DIAMETER_M",
        "PYTHON_VERSION",
        "GENERATION_TIMESTAMP",
    }
    assert set(variables) == expected


def test_generate_variables_values_track_canonical_core() -> None:
    variables = mv.generate_variables()
    assert variables["CONFLICT_CODENAME"] == "CONFLICT STONE"
    assert variables["PROVENANCE_TRANSFERS"] == "5"
    assert variables["PROVENANCE_BREAKPOINTS"] == "2"
    assert variables["PROVENANCE_COVERAGE_PCT"] == "60%"
    assert variables["PROVENANCE_CONFLICT_FREE"] == "false"
    assert variables["CASINO_CASINOS"] == "7"
    assert variables["CASINO_HUB"] == "whyte_house"
    assert variables["CASINO_MONEY_CYCLES"] == "3"
    assert variables["ORBITAL_TARGETS"] == "3"
    assert variables["ORBITAL_VISIBLE_TARGETS"] == "2"
    assert variables["SMUGGLE_CORRIDORS"] == "10"
    assert (
        variables["SMUGGLE_ROUTE"] == "sierra_leone -> nairobi -> paris -> amsterdam -> las_vegas"
    )
    assert variables["SMUGGLE_SURVIVAL_PCT"] == "34%"
    assert variables["LOT_VERDICT"] == "flagrant"
    assert variables["LOT_ANOMALIES"] == "2"
    assert variables["BENFORD_VERDICT"] == "anomalous"
    assert variables["BEAM_MIN_MIRROR_DIAMETER_M"] != ""
    assert "T" in variables["GENERATION_TIMESTAMP"]  # ISO-8601 date-time separator


def test_live_token_cross_reference() -> None:
    """Every {{TOKEN}} used in numbered manuscript sections must be generated."""
    variables = mv.generate_variables()
    for source in sorted(MANUSCRIPT.glob("[0-9][0-9]_*.md")):
        text = source.read_text(encoding="utf-8")
        used = set(_TOKEN_RE.findall(text))
        missing = used - set(variables)
        assert not missing, f"{source.name} uses unknown tokens: {sorted(missing)}"


# ------------------------------------------------------------- config loading


def test_load_config_missing_path_raises() -> None:
    with pytest.raises(FileNotFoundError):
        mv.load_manuscript_config("/no/such/config.yaml")


def test_load_config_non_mapping_raises(tmp_path: Path) -> None:
    config = _write_config(tmp_path / "config.yaml", [1, 2, 3])
    with pytest.raises(TypeError):
        mv.load_manuscript_config(config)


def test_generate_variables_paper_not_mapping_raises(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path / "config.yaml",
        {"paper": "not-a-mapping", "mission": {"film": "x", "codename": "y"}},
    )
    with pytest.raises(TypeError):
        mv.generate_variables(config_path=config)


def test_generate_variables_mission_not_mapping_raises(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path / "config.yaml",
        {"paper": {"title": "T", "subtitle": "S", "version": "1"}, "mission": "x"},
    )
    with pytest.raises(TypeError):
        mv.generate_variables(config_path=config)


# ------------------------------------------------------------- resolve tree


def _seed_manuscript(tmp_path: Path) -> Path:
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir(parents=True, exist_ok=True)
    (manuscript_dir / "00_abstract.md").write_text(
        "Abstract token {{CONFLICT_CODENAME}}.", encoding="utf-8"
    )
    (manuscript_dir / "SYNTAX.md").write_text(
        "Guide with literal {{TOKEN}}. Ignored.", encoding="utf-8"
    )
    return manuscript_dir


def test_resolve_tree_substitutes_and_writes(tmp_path: Path) -> None:
    manuscript_dir = _seed_manuscript(tmp_path)
    variables = mv.generate_variables()
    output_dir, resolved = mv.resolve_manuscript_tree(
        variables, manuscript_dir=manuscript_dir, output_dir=tmp_path / "out"
    )
    assert resolved == ["00_abstract.md"]
    text = (output_dir / "00_abstract.md").read_text(encoding="utf-8")
    assert "CONFLICT STONE" in text
    assert "{{" not in text


def test_resolve_tree_strict_rejects_unresolved(tmp_path: Path) -> None:
    manuscript_dir = _seed_manuscript(tmp_path)
    (manuscript_dir / "01_intro.md").write_text("Bad {{UNKNOWN_TOKEN}} here.", encoding="utf-8")
    with pytest.raises(ValueError):
        mv.resolve_manuscript_tree({}, manuscript_dir=manuscript_dir, output_dir=tmp_path / "out")
    # SYNTAX.md with literal braces is ignored (not a numbered section).


def test_resolve_tree_permissive_allows_unresolved(tmp_path: Path) -> None:
    manuscript_dir = _seed_manuscript(tmp_path)
    (manuscript_dir / "01_intro.md").write_text("Bad {{UNKNOWN_TOKEN}} here.", encoding="utf-8")
    output_dir, resolved = mv.resolve_manuscript_tree(
        {}, manuscript_dir=manuscript_dir, output_dir=tmp_path / "out", strict=False
    )
    assert set(resolved) == {"00_abstract.md", "01_intro.md"}
    leftover = (output_dir / "01_intro.md").read_text(encoding="utf-8")
    assert "{{" in leftover


def test_resolve_tree_empty_dir_raises(tmp_path: Path) -> None:
    empty = tmp_path / "manuscript"
    empty.mkdir(parents=True, exist_ok=True)
    with pytest.raises(FileNotFoundError):
        mv.resolve_manuscript_tree({}, manuscript_dir=empty, output_dir=tmp_path / "out")
