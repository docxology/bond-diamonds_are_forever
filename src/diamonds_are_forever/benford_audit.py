"""Benford's-law laundering detection over the casino ledger (CONFLICT STONE).

Benford's law states that the leading digits of naturally scaled transaction
amounts follow ``p(d) = log10(1 + 1/d)``: a ``1`` appears ~30% of the time, a
``9`` ~4.6%. A laundering operation breaks that pattern by clustering deposits
on round figures.

This module compares a ledger's observed leading-digit distribution against
the Benford expectation with a Pearson chi-square statistic against the
df=8, alpha=0.05 critical value (15.507). A ledger above the critical value is
flagged as anomalous — the laundering signal. Deterministic: pure arithmetic,
no RNG.

**The canonical ledger is a matched control pair.** A detector that fires on
everything detects nothing, so the ledger is built from two separately
inspectable halves:

* :func:`legitimate_ledger_amounts` — the **negative control**. Its leading
  digits are the leading digits of the Fibonacci sequence, which are
  Benford-distributed as a *theorem* (Binet's formula makes ``log10 F_n``
  an irrational rotation, equidistributed mod 1 by Weyl's criterion). The
  baseline therefore conforms because of a property of the sequence, not
  because digit frequencies were hand-picked to pass.
* :func:`laundered_deposit_amounts` — the **positive case**: round-figure cash
  deposits on 1/2/5 x 10^n.

:func:`canonical_ledger_amounts` is their concatenation. Both halves are
constructed fixtures, not empirical records; the pair establishes that this
implementation discriminates between them, not that the screen would separate
real books.
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
    "LEGITIMATE_LEDGER_SIZE",
    "BenfordReport",
    "benford_chi_square",
    "benford_report",
    "canonical_ledger_amounts",
    "digit_contributions",
    "expected_benford_frequency",
    "first_digit",
    "laundered_deposit_amounts",
    "legitimate_ledger_amounts",
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


def digit_contributions(counts: Mapping[int, int]) -> dict[int, float]:
    """Per-digit contribution to the chi-square statistic (empty ledger -> all zero).

    The values sum to :func:`benford_chi_square` of the same counts, so a claim
    like "digit 5 carries most of the statistic" can be derived rather than
    asserted in prose.
    """
    if not isinstance(counts, Mapping):
        raise TypeError("counts must be a mapping of digit -> frequency")
    sample_size = sum(counts.values())
    if sample_size <= 0:
        return {digit: 0.0 for digit in range(1, 10)}
    contributions: dict[int, float] = {}
    for digit in range(1, 10):
        observed = float(counts.get(digit, 0))
        expected = sample_size * expected_benford_frequency(digit)
        contributions[digit] = (observed - expected) * (observed - expected) / expected
    return contributions


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


#: Number of legitimate (negative-control) transactions in the canonical ledger.
LEGITIMATE_LEDGER_SIZE = 80

#: Fibonacci terms skipped before sampling, so every mantissa has four
#: significant digits (F_17 = 1597 is the first four-digit term).
_FIBONACCI_SKIP = 16

#: Decade each successive legitimate amount is placed in, so the baseline spans
#: 10^2..10^4 instead of sitting inside one decade. Scaling by a power of ten
#: leaves the leading digit — and therefore the Benford statistic — untouched.
_DECADE_CYCLE = (2, 3, 4, 3)


def _fibonacci_mantissas(count: int, skip: int) -> tuple[int, ...]:
    """First four significant digits of ``count`` Fibonacci terms after ``skip``.

    Exact integer arithmetic on the Fibonacci recurrence: no floats, so no
    rounding can move a leading digit.
    """
    previous, current = 1, 1
    for _ in range(skip):
        previous, current = current, previous + current
    mantissas: list[int] = []
    for _ in range(count):
        mantissas.append(int(str(previous)[:4]))
        previous, current = current, previous + current
    return tuple(mantissas)


def legitimate_ledger_amounts() -> tuple[float, ...]:
    """The legitimate half of the ledger — the audit's negative control.

    Amounts are Fibonacci mantissas placed across the 10^2..10^4 decades. The
    leading digits of the Fibonacci sequence are Benford-distributed by
    theorem, so this baseline conforms for a reason external to the audit:
    nothing here was tuned against the chi-square statistic, and decade
    placement cannot change a leading digit.

    Without this half the package would only ever have shown the test firing,
    which is compatible with a test that fires on everything.
    """
    amounts: list[float] = []
    for index, mantissa in enumerate(_fibonacci_mantissas(LEGITIMATE_LEDGER_SIZE, _FIBONACCI_SKIP)):
        exponent = _DECADE_CYCLE[index % len(_DECADE_CYCLE)] - 3
        if exponent >= 0:
            amounts.append(float(mantissa * 10**exponent))
        else:
            amounts.append(mantissa / float(10**-exponent))
    return tuple(amounts)


def laundered_deposit_amounts() -> tuple[float, ...]:
    """The laundered half — 61 round-figure cash deposits on 1/2/5 x 10^n.

    Structuring cash into round figures is exactly what forensic digit
    analysis is built to surface: the leading digits collapse onto 1, 2, and 5
    and no other digit appears at all.
    """
    return (
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


def canonical_ledger_amounts() -> tuple[float, ...]:
    """The canonical CONFLICT STONE casino ledger: baseline plus laundered cash.

    The concatenation of :func:`legitimate_ledger_amounts` (which conforms on
    its own) and :func:`laundered_deposit_amounts` (which does not). The
    combined statistic exceeds the critical value, and because the baseline
    passes alone, the flag is attributable to the deposits.
    """
    return legitimate_ledger_amounts() + laundered_deposit_amounts()
