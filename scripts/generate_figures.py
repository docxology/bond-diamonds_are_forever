#!/usr/bin/env python3
"""Thin orchestrator: render the CONFLICT STONE figures under output/figures/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from diamonds_are_forever.figures import generate_all_figures


def main() -> int:
    figures_dir = ROOT / "output" / "figures"
    paths = generate_all_figures(figures_dir)
    for path in paths:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
