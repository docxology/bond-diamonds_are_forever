"""Shared pytest fixtures for diamonds_are_forever (CONFLICT STONE).

- Forces the non-interactive matplotlib backend so figure tests never open a
  display window.
- Ensures ``src/`` is importable for BOND discovery regardless of install state.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

__all__: list[str] = []
