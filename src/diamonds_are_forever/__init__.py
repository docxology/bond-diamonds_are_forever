"""diamonds_are_forever — BOND film package · mission codename CONFLICT STONE.

Pure domain core for *Diamonds Are Forever* (1971): deterministic analysis of
a smuggled-goods provenance chain, a Las Vegas casino money-movement network,
and an orbital space-mirror targeting geometry. The pure modules are
infrastructure-free and importable without BOND-API; ``mission.py`` is the thin
adapter that implements the frozen :class:`bond_api.protocol.MissionProvider`.

Modules
-------
- :mod:`~diamonds_are_forever.provenance_chain` — conflict-diamond custody
  graph, documented handoffs, provenance break points.
- :mod:`~diamonds_are_forever.casino_network` — Las Vegas casino money
  movement: gross flow, net positions, laundering closure, hub casino.
- :mod:`~diamonds_are_forever.orbital_mirror` — space-mirror orbital targeting
  geometry: line-of-sight, slant range, beam delivery.
- :mod:`~diamonds_are_forever.mission` — ``MissionProvider`` adapter.
"""

from __future__ import annotations

__version__ = "0.1.0"

#: The film package identity (BOND slug this mission answers to).
FILM = "diamonds_are_forever"
#: The mission codename.
CODENAME = "CONFLICT STONE"

__all__ = ["CODENAME", "FILM", "__version__"]
