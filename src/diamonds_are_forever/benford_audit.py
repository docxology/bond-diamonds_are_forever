"""Benford's-law laundering detection over the casino ledger (CONFLICT STONE).

Benford's law states that the leading digits of natural transaction amounts
follow ``p(d) = log10(1 + 1/d)``: a ``1`` appears ~30% of the time, a ``9``
~4.6%. Money-laundering operations break the pattern twice over — the
laundered deposits cluster at round figures, and the (fabricated) "legitimate"
amounts rarely span a natural magnitude range.

This module compares a ledger's observed leading-digit distribution against
the Benford expectation with a Pearson chi-square statistic against the
df=8, alpha=0.05 critical value (15.507). A ledger above the critical value is
flagged as anomalous — the laundering signal. Deterministic: pure arithmetic,
no RNG.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

__all__ = [
    "BENFORD_ALPHA",
    "BENFORD_CRITICAL_VALUE_05",
    "BENFORD_DEGREES_OF_FREEDOM",
    "BenfordReport",
    "benford_chi_square",
    "benford_report",
    "canonical_ledger_amounts",
    "expected_benford_frequency",
    "first_digit",
]

#: chi-square critical value, df=8, alpha=0.05.
BENFORD_CRITICAL_VALUE_05 = 15.507
#: Degrees of freedom of the leading-digit test (nine digit classes minus one).
BENFORD_DEGREES_OF_FREEDOM = 8
#: Significance level the critical value is taken at.
BENFORD_ALPHA = 0.05


@dataclass(frozen=True)
class BenfordReport:
    """The deterministic outcome of a Benford audit of a ledger."""

    transactions: int
    chi_square: float
    critical_value: float
    conforms: bool
    distribution: dict[str, int]


def first_digit(value: float) -> int:
    """Leading digit (1-9) of a positive number.

    The digit is derived by exact integer arithmetic on the value's rational
    representation, deliberately avoiding two tempting shortcuts:

    * **iterative scaling** (``while m < 1.0: m *= 10.0``) re-rounds on every
      step, so error compounds across the exponent range and small magnitudes
      drift into the neighbouring digit — ``1e-300`` scales to
      ``9.999999999999993`` and reads as a 9;
    * **formatted output** (``f"{v:.17e}"[0]``) *rounds* the mantissa, so a
      value whose exact expansion is ``6.999999999999999999e-304`` reads as a
      7.

    Scaling ``as_integer_ratio()`` in exact integers has neither failure mode.
    Note the semantics this fixes: the digit describes the ``float`` actually
    held, so a decimal literal whose nearest double sits just below a power of
    ten (``7e-304`` is stored as ``6.9999...e-304``) reads as the lower digit.
    That is the correct statement about the number the program is auditing.
    Benford's law is defined by truncation, so no rounding is applied anywhere.

    Raises:
        TypeError: if ``value`` is not a number.
        ValueError: if ``value`` is not positive.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError("value must be a non-boolean number")
    if value <= 0:
        raise ValueError("first digit is undefined for non-positive values")
    numerator, denominator = abs(float(value)).as_integer_ratio()
    while numerator >= 10 * denominator:
        denominator *= 10
    while numerator < denominator:
        numerator *= 10
    return numerator // denominator


def expected_benford_frequency(digit: int) -> float:
    """Benford expectation ``log10(1 + 1/digit)`` for a leading digit."""
    if not isinstance(digit, int) or isinstance(digit, bool) or not 1 <= digit <= 9:
        raise ValueError("digit must be an integer within [1, 9]")
    return float(math.log10(1.0 + 1.0 / digit))


def benford_chi_square(counts: Mapping[int, int]) -> float:
    """Pearson chi-square of the observed digit counts against Benford (0.0 if empty)."""
    if not isinstance(counts, Mapping):
        raise TypeError("counts must be a mapping of digit -> frequency")
    sample_size = sum(counts.values())
    if sample_size <= 0:
        return 0.0
    statistic = 0.0
    for digit in range(1, 10):
        observed = float(counts.get(digit, 0))
        expected = sample_size * expected_benford_frequency(digit)
        statistic += (observed - expected) * (observed - expected) / expected
    return statistic


def benford_report(amounts: Sequence[float]) -> BenfordReport:
    """Audit a ledger against Benford's law.

    Non-positive amounts are ignored (they have no leading digit). Returns a
    deterministic :class:`BenfordReport` with the transaction count, the
    chi-square statistic, the critical value, a ``conforms`` verdict, and the
    digit distribution.
    """
    if not isinstance(amounts, Sequence):
        raise TypeError("amounts must be a sequence of numbers")
    counts: Counter[int] = Counter()
    for amount in amounts:
        if isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount > 0:
            counts[first_digit(amount)] += 1
    statistic = benford_chi_square(counts)
    return BenfordReport(
        transactions=int(sum(counts.values())),
        chi_square=round(statistic, 4),
        critical_value=BENFORD_CRITICAL_VALUE_05,
        conforms=statistic <= BENFORD_CRITICAL_VALUE_05,
        distribution={str(digit): int(counts.get(digit, 0)) for digit in range(1, 10)},
    )


def canonical_ledger_amounts() -> tuple[float, ...]:
    """The canonical CONFLICT STONE casino ledger (101 transactions).

    Forty varied "natural" amounts sit beside sixty-one suspiciously round
    deposits (laundered cash) clustered on 10^4/2x10^4/5x10^4-style figures,
    so the leading digits skew toward 1, 2, and 5 and the chi-square statistic
    exceeds the critical value — the laundering signal the audit must catch.
    """
    natural = (
        4123.0,
        7610.5,
        2890.0,
        9301.0,
        1542.75,
        6734.0,
        5820.0,
        3187.5,
        8290.0,
        2460.0,
        1975.0,
        7340.0,
        5105.0,
        9990.0,
        8630.0,
        3205.0,
        4480.0,
        6710.0,
        2530.0,
        7805.0,
        6100.0,
        5390.0,
        4240.0,
        8990.0,
        9760.0,
        3520.0,
        4680.0,
        7150.0,
        8330.0,
        2940.0,
        1250.0,
        6840.0,
        7315.0,
        5520.0,
        9180.0,
        4040.0,
        3750.0,
        6290.0,
        8960.0,
        1450.0,
    )
    round_deposits = (
        *(10000.0,) * 10,
        *(20000.0,) * 10,
        *(50000.0,) * 10,
        *(100000.0,) * 6,
        *(200000.0,) * 6,
        *(500000.0,) * 6,
        *(1_000_000.0,) * 4,
        *(2_000_000.0,) * 4,
        *(5_000_000.0,) * 4,
        10_000_000.0,
    )
    return natural + round_deposits
