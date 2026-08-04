#!/usr/bin/env python3
"""Thin orchestrator: execute the CONFLICT STONE plan and print the outcome."""

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
    outcome = provider.execute(provider.plan(provider.brief()))
    print(f"Success: {outcome.success}")
    print("Results:")
    for key, value in outcome.results.items():
        print(f"  - {key}: {value}")
    print(
        f"Provenance: v{outcome.provenance.package_version} seed={outcome.provenance.seed} "
        f"input_hash={outcome.provenance.input_hash[:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
