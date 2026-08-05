#!/usr/bin/env python3
"""Thin orchestrator: run the full CONFLICT STONE mission flow end-to-end.

Walks a provider through brief -> recon -> plan -> execute -> debrief and
prints a deterministic summary plus the outcome as round-trip JSON.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bond_api.protocol import ReconRequest, run_mission
from bond_api.serialization import to_json

from diamonds_are_forever.mission import CODENAME, MissionProvider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the outcome as round-trip JSON")
    args = parser.parse_args()

    provider = MissionProvider()
    debrief = run_mission(provider, ReconRequest(goal="survey domains and execute the audit"))
    outcome = debrief.outcome
    print(f"Film: {provider.film} ({CODENAME})")
    print(f"Package version: {outcome.provenance.package_version}")
    print(f"Success: {outcome.success}")
    print(f"Input hash: {outcome.provenance.input_hash}")
    print(f"Lessons: {len(debrief.lessons)}")
    if args.json:
        print(to_json(outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
