"""diamonds_are_forever — BOND film package · mission codename CONFLICT STONE.

Pure domain core for *Diamonds Are Forever* (1971): deterministic analysis of
a smuggled-goods provenance chain and its smuggling corridors, the physical
forensics of the diamond lot, a Las Vegas casino money-movement network and its
Benford ledger signature, and an orbital space-mirror's targeting geometry and
beam-delivery physics. The seven pure modules are infrastructure-free and
importable without BOND-API; ``mission.py`` is the thin adapter that implements
the frozen :class:`bond_api.protocol.MissionProvider`.

Pure domain modules
-------------------
- :mod:`~diamonds_are_forever.provenance_chain` — conflict-diamond custody
  graph, documented handoffs, provenance break points, origin tracing.
- :mod:`~diamonds_are_forever.smuggling_routes` — risk-weighted corridor
  network; expected-cost Dijkstra optimum vs. a fewest-hops BFS baseline.
- :mod:`~diamonds_are_forever.lot_forensics` — weight-gain / excessive-loss /
  density-mismatch audit of a lot, with a clean/suspicious/flagrant verdict.
- :mod:`~diamonds_are_forever.casino_network` — Las Vegas casino money
  movement: gross flow, net positions, money cycles, laundering closure, hub.
- :mod:`~diamonds_are_forever.benford_audit` — leading-digit Benford law and
  the Pearson chi-square verdict over the casino ledger.
- :mod:`~diamonds_are_forever.orbital_mirror` — space-mirror targeting
  geometry: occultation, slant range, elevation, captured power.
- :mod:`~diamonds_are_forever.beam_physics` — diffraction spot, Beer-Lambert
  attenuation, power budget, vaporization dwell, minimum mirror diameter.

Adapter and manifest modules
----------------------------
- :mod:`~diamonds_are_forever.mission` — the frozen ``MissionProvider``
  adapter and the ``register_gadgets`` hook.
- :mod:`~diamonds_are_forever.manuscript_variables` — ``{{TOKEN}}`` hydration
  from ``manuscript/config.yaml`` plus the live core.
- :mod:`~diamonds_are_forever.figures` — deterministic matplotlib figures.
"""

from __future__ import annotations

__version__ = "0.1.0"

#: The film package identity (BOND slug this mission answers to).
FILM = "diamonds_are_forever"
#: The mission codename.
CODENAME = "CONFLICT STONE"

__all__ = ["CODENAME", "FILM", "__version__"]
