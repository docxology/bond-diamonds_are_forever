"""Diamond-lot weight & density reconciliation forensics (CONFLICT STONE deepening).

Beyond the paperwork break points, a smuggling operation must launder the
*physical* lot: stones are cut (legitimate weight loss), stolen (excessive
weight loss), or swapped for paste (a substitution that keeps weight but not
density). This module audits one lot's handoff samples against three
forensic rules:

* **weight gain** — a shipped weight above the received weight is physically
  impossible for a genuine lot (accounting fraud / substitution);
* **excessive loss** — a loss beyond the legitimate cutting allowance implies
  theft or diversion;
* **density mismatch** — a measured density outside the diamond window
  (3.40-3.65 g/cm3 around the nominal 3.52) identifies a paste or simulant
  substitution.

Each violation contributes to an audit score and a lot verdict
(``clean`` / ``suspicious`` / ``flagrant``). Deterministic: pure float
comparisons, no RNG.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DIAMOND_DENSITY_G_CM3",
    "AuditReport",
    "HandoffSample",
    "LotForensicError",
    "audit_lot",
    "canonical_lot_samples",
]

#: Nominal diamond density (g/cm3).
DIAMOND_DENSITY_G_CM3 = 3.52
#: Weight tolerance below which a delta is treated as exact.
_EPSILON = 1e-9
#: Anomaly severity weights.
_WEIGHT_GAIN_SCORE = 2
_EXCESSIVE_LOSS_SCORE = 1
_DENSITY_MISMATCH_SCORE = 3


class LotForensicError(ValueError):
    """Raised for invalid lot samples or audit inputs."""


@dataclass(frozen=True)
class HandoffSample:
    """One handoff's declared weights and the measured density of the lot."""

    lot: str
    from_actor: str
    to_actor: str
    weight_in_g: float
    weight_out_g: float
    measured_density_g_cm3: float = DIAMOND_DENSITY_G_CM3
    note: str = ""

    def __post_init__(self) -> None:
        for label, value in (
            ("lot", self.lot),
            ("from_actor", self.from_actor),
            ("to_actor", self.to_actor),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"HandoffSample.{label} must be a non-empty string")
        for number_label, number_value in (
            ("weight_in_g", self.weight_in_g),
            ("weight_out_g", self.weight_out_g),
        ):
            if not isinstance(number_value, (int, float)) or isinstance(number_value, bool):
                raise TypeError(f"HandoffSample.{number_label} must be a non-boolean number")
            if number_value < 0:
                raise ValueError(f"HandoffSample.{number_label} cannot be negative")
        if not isinstance(self.measured_density_g_cm3, (int, float)) or isinstance(
            self.measured_density_g_cm3, bool
        ):
            raise TypeError("HandoffSample.measured_density_g_cm3 must be a non-boolean number")
        if self.measured_density_g_cm3 <= 0:
            raise ValueError("HandoffSample.measured_density_g_cm3 must be positive")


@dataclass(frozen=True)
class AuditReport:
    """The forensic outcome for one lot: per-step deltas, flags, and verdict."""

    samples: tuple[HandoffSample, ...]
    deltas_g: tuple[float, ...]
    flags: tuple[str, ...]
    anomalies: tuple[tuple[int, str, str], ...]
    score: int
    verdict: str


def audit_lot(
    samples: list[HandoffSample] | tuple[HandoffSample, ...],
    *,
    cutting_loss_limit: float = 0.25,
    density_min: float = 3.40,
    density_max: float = 3.65,
) -> AuditReport:
    """Audit a lot's handoff samples and return a deterministic forensic report.

    Args:
        samples: The handoff samples in chain order.
        cutting_loss_limit: Maximum legitimate fractional weight loss per handoff.
        density_min / density_max: The genuine-diamond density window (g/cm3).

    Raises:
        LotForensicError: if the sample set is empty.
        TypeError: if an entry is not a :class:`HandoffSample`.
    """
    if not isinstance(samples, (list, tuple)):
        raise TypeError("samples must be a sequence of HandoffSample")
    validated = tuple(samples)
    if not validated:
        raise LotForensicError("a lot audit needs at least one handoff sample")
    for sample in validated:
        if not isinstance(sample, HandoffSample):
            raise TypeError("samples entries must be HandoffSample instances")
    if cutting_loss_limit < 0:
        raise LotForensicError("cutting_loss_limit cannot be negative")
    if not density_min < density_max:
        raise LotForensicError("density_min must be below density_max")

    deltas: list[float] = []
    flags: list[str] = []
    anomalies: list[tuple[int, str, str]] = []
    for index, sample in enumerate(validated):
        delta = sample.weight_in_g - sample.weight_out_g
        deltas.append(delta)
        flag = ""
        if delta < -_EPSILON:
            flag = "weight_gain"
            anomalies.append(
                (
                    index,
                    "weight_gain",
                    f"shipped {sample.weight_out_g:.2f}g exceeds received {sample.weight_in_g:.2f}g",
                )
            )
        elif delta > cutting_loss_limit * sample.weight_in_g:
            flag = "excessive_loss"
            anomalies.append(
                (
                    index,
                    "excessive_loss",
                    f"loss of {delta:.2f}g exceeds the {cutting_loss_limit:.0%} cutting allowance",
                )
            )
        if not density_min <= sample.measured_density_g_cm3 <= density_max:
            flag = f"{flag};density_mismatch" if flag else "density_mismatch"
            anomalies.append(
                (
                    index,
                    "density_mismatch",
                    f"measured {sample.measured_density_g_cm3:.2f} g/cm3 outside [{density_min:.2f}, {density_max:.2f}]",
                )
            )
        flags.append(flag)

    score = 0
    for _index, code, _detail in anomalies:
        if code == "weight_gain":
            score += _WEIGHT_GAIN_SCORE
        elif code == "excessive_loss":
            score += _EXCESSIVE_LOSS_SCORE
        elif code == "density_mismatch":
            score += _DENSITY_MISMATCH_SCORE
    verdict = "clean" if not anomalies else ("suspicious" if len(anomalies) == 1 else "flagrant")
    return AuditReport(
        samples=validated,
        deltas_g=tuple(deltas),
        flags=tuple(flags),
        anomalies=tuple(anomalies),
        score=score,
        verdict=verdict,
    )


def canonical_lot_samples() -> tuple[HandoffSample, ...]:
    """The canonical CONFLICT STONE lot ``DF-71``.

    The lot is cut legally once (20% loss within the 25% allowance), then the
    Amsterdam handoff swaps it for paste (density 2.50), and the final leg
    loses 60% of its weight — the theft that closes the operation.
    """
    return (
        HandoffSample(
            "DF-71", "sierra_leone_mine", "illicit_broker", 14.0, 14.0, note="wildcat handoff"
        ),
        HandoffSample(
            "DF-71", "illicit_broker", "nairobi_courier", 14.0, 11.2, note="rough cutting"
        ),
        HandoffSample(
            "DF-71", "nairobi_courier", "london_dealer", 11.2, 11.2, note="doctored papers"
        ),
        HandoffSample(
            "DF-71",
            "london_dealer",
            "amsterdam_contact",
            11.2,
            11.2,
            measured_density_g_cm3=2.50,
            note="paste swap",
        ),
        HandoffSample(
            "DF-71", "amsterdam_contact", "las_vegas_fence", 11.2, 4.5, note="diverted consignment"
        ),
    )
