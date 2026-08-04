#!/usr/bin/env python3
"""Thin orchestrator: print the CONFLICT STONE mission plan (plan phase)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from diamonds_are_forever.mission import MissionProvider


def main() -> int:
    provider = MissionProvider()
    plan = provider.plan(provider.brief())
    print(f"Plan steps: {len(plan.steps)}")
    for step in plan.steps:
        print(f"  - [{step.name}] {step.action} {step.params}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
