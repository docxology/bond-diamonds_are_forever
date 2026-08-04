"""Subprocess smoke tests for the CONFLICT STONE phase CLIs (no mocks)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

PHASE_EXPECT = {
    "brief.py": ("Objectives:", "Constraints:", "Assets:"),
    "recon.py": ("chain:", "casinos:"),
    "plan.py": ("analyze_custody_chain", "solve_targeting_geometry"),
    "execute.py": ("Success: True", "input_hash="),
    "debrief.py": ("Outcome success: True", "Lessons:"),
}


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_each_phase_script_exits_zero_and_prints() -> None:
    for script, needles in PHASE_EXPECT.items():
        result = _run(script)
        assert result.returncode == 0, f"{script} failed: {result.stderr}"
        for needle in needles:
            assert needle in result.stdout, f"{script} stdout missing {needle!r}"


def test_run_mission_full_flow() -> None:
    result = _run("run_mission.py")
    assert result.returncode == 0
    assert "Success: True" in result.stdout
    assert "Input hash:" in result.stdout


def test_run_mission_json() -> None:
    result = _run("run_mission.py", "--json")
    assert result.returncode == 0
    assert '"__bond_type__": "MissionOutcome"' in result.stdout


def test_generate_figures_writes_pngs(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "generate_figures.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    for name in ("provenance_chain.png", "casino_network.png", "orbital_visibility.png"):
        assert (ROOT / "output" / "figures" / name).is_file()


def test_generate_manuscript_variables_hydrates_tree() -> None:
    result = _run("z_generate_manuscript_variables.py")
    assert result.returncode == 0, result.stderr
    assert "Resolved" in result.stdout
    data = ROOT / "output" / "data" / "manuscript_variables.json"
    assert data.is_file()
    import json

    variables = json.loads(data.read_text(encoding="utf-8"))
    assert variables["CONFLICT_CODENAME"] == "CONFLICT STONE"
