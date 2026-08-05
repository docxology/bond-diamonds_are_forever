"""Tests for manuscript variable hydration + the live {{TOKEN}} cross-reference gate."""

from __future__ import annotations

import datetime as dt
import hashlib
import math
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest
import yaml

from diamonds_are_forever import (
    beam_physics,
    benford_audit,
    lot_forensics,
    orbital_mirror,
    smuggling_routes,
)
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
        "SMUGGLE_NAIVE_ROUTE",
        "SMUGGLE_CARGO_VALUE_M",
        "SMUGGLE_EXPECTED_COST_M",
        "SMUGGLE_NAIVE_COST_M",
        "SMUGGLE_SURVIVAL_PCT",
        "SMUGGLE_EXPOSURE_PCT",
        "SMUGGLE_REDUCTION_PCT",
        "LOT_ID",
        "LOT_SAMPLES",
        "LOT_ANOMALIES",
        "LOT_AUDIT_SCORE",
        "LOT_VERDICT",
        "LOT_CUTTING_ALLOWANCE_PCT",
        "LOT_DENSITY_NOMINAL",
        "LOT_DENSITY_MIN",
        "LOT_DENSITY_MAX",
        "CASINO_CASINOS",
        "CASINO_TRANSFERS",
        "CASINO_TOTAL_FLOW_M",
        "CASINO_HUB",
        "CASINO_MONEY_CYCLES",
        "CASINO_LAUNDERING_CLOSURE_PCT",
        "BENFORD_TRANSACTIONS",
        "BENFORD_CHI_SQUARE",
        "BENFORD_CRITICAL_VALUE",
        "BENFORD_ALPHA",
        "BENFORD_DF",
        "BENFORD_VERDICT",
        "BENFORD_LEGIT_TRANSACTIONS",
        "BENFORD_LEGIT_CHI_SQUARE",
        "BENFORD_LEGIT_VERDICT",
        "BENFORD_LAUNDERED_TRANSACTIONS",
        "BENFORD_CARRIER_DIGIT",
        "BENFORD_CARRIER_SHARE_PCT",
        "ORBITAL_ALTITUDE_KM",
        "ORBITAL_TARGETS",
        "ORBITAL_VISIBLE_TARGETS",
        "ORBITAL_VISIBLE_NAMES",
        "ORBITAL_OCCULTED_NAMES",
        "BEAM_MIRROR_DIAMETER_M",
        "BEAM_WAVELENGTH_NM",
        "BEAM_SLANT_RANGE_KM",
        "BEAM_TRANSMITTANCE_PCT",
        "BEAM_SPOT_RADIUS_M",
        "BEAM_IRRADIANCE_W_M2",
        "BEAM_CONCENTRATION_X",
        "BEAM_VAPORIZE_TIME_S",
        "BEAM_REQUIRED_IRRADIANCE_MW",
        "BEAM_MIN_MIRROR_DIAMETER_M",
        "PYTHON_VERSION",
        "MANUSCRIPT_DATE",
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
    # The negative control must be reported as conforming, or the anomalous
    # verdict above is not attributable to the laundered deposits.
    assert variables["BENFORD_LEGIT_VERDICT"] == "conforms"
    assert float(variables["BENFORD_LEGIT_CHI_SQUARE"]) < benford_audit.BENFORD_CRITICAL_VALUE_05
    assert float(variables["BENFORD_CHI_SQUARE"]) > benford_audit.BENFORD_CRITICAL_VALUE_05
    assert int(variables["BENFORD_TRANSACTIONS"]) == int(
        variables["BENFORD_LEGIT_TRANSACTIONS"]
    ) + int(variables["BENFORD_LAUNDERED_TRANSACTIONS"])
    assert variables["BEAM_MIN_MIRROR_DIAMETER_M"] != ""
    # The manuscript stamp is the committed config value, not a clock reading.
    config = mv.load_manuscript_config()
    assert variables["MANUSCRIPT_DATE"] == str(config["paper"]["date"])


def test_model_constant_tokens_track_the_core_constants() -> None:
    """Tokens that stand in for model constants must be derived, not restated."""
    variables = mv.generate_variables()
    assert variables["LOT_ID"] == lot_forensics.CANONICAL_LOT_ID
    assert variables["LOT_CUTTING_ALLOWANCE_PCT"] == f"{lot_forensics.CUTTING_LOSS_LIMIT:.0%}"
    assert variables["LOT_DENSITY_MIN"] == f"{lot_forensics.DENSITY_MIN_G_CM3:.2f}"
    assert variables["LOT_DENSITY_MAX"] == f"{lot_forensics.DENSITY_MAX_G_CM3:.2f}"
    assert variables["LOT_DENSITY_NOMINAL"] == f"{lot_forensics.DIAMOND_DENSITY_G_CM3:.2f}"
    assert variables["BENFORD_DF"] == str(benford_audit.BENFORD_DEGREES_OF_FREEDOM)
    assert variables["BENFORD_ALPHA"] == f"{benford_audit.BENFORD_ALPHA:g}"
    assert variables["BENFORD_CRITICAL_VALUE"] == f"{benford_audit.BENFORD_CRITICAL_VALUE_05:.3f}"
    assert variables["BEAM_REQUIRED_IRRADIANCE_MW"] == (
        f"{beam_physics.REQUIRED_STRIKE_IRRADIANCE_W_M2 / 1.0e6:g}"
    )
    assert variables["BEAM_MIRROR_DIAMETER_M"] == (
        f"{beam_physics.canonical_beam_scenario().mirror_diameter_m:.0f}"
    )
    assert variables["SMUGGLE_CARGO_VALUE_M"] == (
        f"{smuggling_routes.canonical_cargo_value_m():.1f}"
    )


def test_visible_and_occulted_names_partition_the_targets() -> None:
    """Every canonical target is reported exactly once, as visible or occulted."""
    variables = mv.generate_variables()
    visible = [n for n in variables["ORBITAL_VISIBLE_NAMES"].split(", ") if n]
    occulted = [n for n in variables["ORBITAL_OCCULTED_NAMES"].split(", ") if n]
    all_names = [target.name for target in orbital_mirror.canonical_targets()]
    assert sorted(visible + occulted) == sorted(all_names)
    assert not set(visible) & set(occulted)
    assert variables["ORBITAL_VISIBLE_TARGETS"] == str(len(visible))


def test_naive_route_is_never_cheaper_than_the_optimum() -> None:
    """The reduction token can only be non-negative — same graph, same endpoints."""
    variables = mv.generate_variables()
    assert float(variables["SMUGGLE_NAIVE_COST_M"]) >= float(variables["SMUGGLE_EXPECTED_COST_M"])
    assert not variables["SMUGGLE_REDUCTION_PCT"].startswith("-")


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


# ------------------------------------------------------------- pinned date stamp


def test_pinned_manuscript_date_accepts_a_quoted_string() -> None:
    assert mv.pinned_manuscript_date({"date": "2026-08-04"}) == "2026-08-04"


def test_pinned_manuscript_date_normalises_a_yaml_date_object() -> None:
    """Unquoted YAML ``date:`` parses to ``datetime.date`` — still ISO, still pinned."""
    assert mv.pinned_manuscript_date({"date": dt.date(2026, 8, 4)}) == "2026-08-04"
    stamped = dt.datetime(2026, 8, 4, 12, 30, tzinfo=dt.timezone.utc)
    assert mv.pinned_manuscript_date({"date": stamped}) == "2026-08-04T12:30:00+00:00"


def test_pinned_manuscript_date_missing_fails_loudly() -> None:
    """A missing stamp must raise, never silently fall back to the clock."""
    with pytest.raises(ValueError):
        mv.pinned_manuscript_date({"title": "no date here"})


# ------------------------------------------------------- regeneration determinism

SCRIPT = ROOT / "scripts" / "z_generate_manuscript_variables.py"


def _run_generator(output_dir: Path) -> None:
    """Run the real orchestrator — the production entry point, not a re-implementation."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(output_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def _digest_tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _sleep_past_the_next_whole_second() -> None:
    """Straddle a second boundary so a seconds-resolution clock would differ.

    Without this the two runs can land inside the same second and a wall-clock
    stamp would compare equal by luck — the determinism assertion would pass
    while proving nothing.
    """
    now = time.time()
    time.sleep(math.floor(now) + 1.05 - now)


def test_regeneration_is_byte_identical_across_a_second_boundary(tmp_path: Path) -> None:
    """Two full regenerations must write identical bytes.

    This is the claim made in ``manuscript/06_reproducibility.md``, ``AGENTS.md``,
    ``STANDALONE.md`` and ``docs/agent_instructions.md``. It runs the generator
    twice for real, separated by a whole-second boundary, so reintroducing any
    wall-clock value into a persisted artifact turns this test red.
    """
    first, second = tmp_path / "run1", tmp_path / "run2"

    _run_generator(first)
    _sleep_past_the_next_whole_second()
    _run_generator(second)

    before, after = _digest_tree(first), _digest_tree(second)

    # Non-vacuity: the comparison is meaningless unless real artifacts landed.
    assert "data/manuscript_variables.json" in before
    assert "manuscript/05_experimental_setup.md" in before
    assert len(before) >= 10
    assert set(before) == set(after)

    differing = sorted(name for name in before if before[name] != after[name])
    assert not differing, f"regeneration is not byte-identical: {differing}"
