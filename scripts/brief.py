#!/usr/bin/env python3
"""Thin orchestrator: print the CONFLICT STONE mission brief (brief phase)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from diamonds_are_forever.mission import MissionProvider


def main() -> int:
    brief = MissionProvider().brief()
    print(f"Film: {brief.film} ({brief.codename})")
    print("Objectives:")
    for objective in brief.objectives:
        print(f"  - {objective}")
    print(f"Assets: {len(brief.assets)}")
    for asset in brief.assets:
        print(f"  - [{asset.kind}] {asset.name}: {asset.payload}")
    print(f"Constraints: {len(brief.constraints)}")
    for constraint in brief.constraints:
        print(f"  - {constraint.kind}: {constraint.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
