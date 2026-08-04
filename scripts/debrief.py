#!/usr/bin/env python3
"""Thin orchestrator: run the CONFLICT STONE debrief and print lessons."""

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
    debrief = provider.debrief(provider.execute(provider.plan(provider.brief())))
    print(f"Outcome success: {debrief.outcome.success}")
    print("Lessons:")
    for lesson in debrief.lessons:
        print(f"  - {lesson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
