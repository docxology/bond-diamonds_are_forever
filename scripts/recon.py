#!/usr/bin/env python3
"""Thin orchestrator: run the CONFLICT STONE recon phase and print findings."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bond_api.protocol import ReconRequest

from diamonds_are_forever.mission import MissionProvider


def main() -> int:
    report = MissionProvider().recon(ReconRequest(goal="survey available assets and constraints"))
    print("Recon findings:")
    for finding in report.findings:
        print(f"  - {finding.label}: {finding.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
