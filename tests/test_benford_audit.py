"""Tests for Benford's-law laundering detection (deterministic, no mocks)."""

from __future__ import annotations

import math
from decimal import Decimal

import pytest

from diamonds_are_forever import benford_audit as ba
from diamonds_are_forever.benford_audit import (
    BENFORD_CRITICAL_VALUE_05,
    benford_chi_square,
    benford_report,
    canonical_ledger_amounts,
    expected_benford_frequency,
    first_digit,
)

# -------------------------------------------------------------- first_digit


def test_first_digit_known_values() -> None:
    assert first_digit(1) == 1
    assert first_digit(9) == 9
    assert first_digit(10) == 1
    assert first_digit(100) == 1
    assert first_digit(4123.0) == 4
    assert first_digit(0.05) == 5
    assert first_digit(9_999.0) == 9


def test_first_digit_rejects_non_positive() -> None:
    with pytest.raises(ValueError):
        first_digit(0)
    with pytest.raises(ValueError):
        first_digit(-3.0)


def test_first_digit_rejects_non_number() -> None:
    with pytest.raises(TypeError):
        first_digit("4")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        first_digit(True)  # type: ignore[arg-type]


# ------------------------------------------------------------- benford pdf


def test_expected_benford_frequency() -> None:
    assert expected_benford_frequency(1) == pytest.approx(math.log10(2.0))
    assert expected_benford_frequency(9) == pytest.approx(math.log10(10.0 / 9.0))
    # digit 1 is ~30%, digit 9 ~4.6%
    assert expected_benford_frequency(1) > expected_benford_frequency(9)
    assert expected_benford_frequency(1) == pytest.approx(0.3010, rel=0.01)


def test_expected_benford_frequency_rejects_bad_digit() -> None:
    with pytest.raises(ValueError):
        expected_benford_frequency(0)
    with pytest.raises(ValueError):
        expected_benford_frequency(10)
    with pytest.raises(ValueError):
        expected_benford_frequency(True)


# ------------------------------------------------------------- chi-square


def test_benford_chi_square_empty_is_zero() -> None:
    assert benford_chi_square({}) == 0.0


def test_benford_chi_square_behind_a_law_conforming_ledger_is_small() -> None:
    counts = {1: 30, 2: 18, 3: 12, 4: 10, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4}
    assert benford_chi_square(counts) < 20.0


def test_benford_chi_square_single_digit_ledger_is_huge() -> None:
    # 100 deposits all leading with 1: strongly non-Benford.
    statistic = benford_chi_square({1: 100})
    assert statistic > BENFORD_CRITICAL_VALUE_05


def test_benford_chi_square_rejects_non_mapping() -> None:
    with pytest.raises(TypeError):
        benford_chi_square([1, 2, 3])  # type: ignore[arg-type]


# ------------------------------------------------------------------ report


def test_canonical_ledger_is_anomalous() -> None:
    report = benford_report(canonical_ledger_amounts())
    assert report.transactions == 101
    assert report.chi_square > BENFORD_CRITICAL_VALUE_05
    assert report.conforms is False
    assert report.critical_value == BENFORD_CRITICAL_VALUE_05


def test_canonical_distribution_sums_to_transactions() -> None:
    report = benford_report(canonical_ledger_amounts())
    assert sum(report.distribution.values()) == report.transactions


def test_benford_report_ignores_non_positive_amounts() -> None:
    report = benford_report((-5.0, 0.0, 3.0, 30.0))
    assert report.transactions == 2
    assert report.distribution["3"] == 2


def test_benford_report_all_round_numbers_is_anomalous() -> None:
    report = benford_report(tuple(10_000.0 for _ in range(50)))
    assert report.conforms is False


def test_benford_report_deterministic() -> None:
    assert benford_report(canonical_ledger_amounts()) == benford_report(canonical_ledger_amounts())


def test_benford_report_rejects_non_sequence() -> None:
    with pytest.raises(TypeError):
        benford_report(17)  # type: ignore[arg-type]


def _exact_leading_digit(value: float) -> int:
    """Independent oracle: leading digit of the float's exact binary value.

    ``Decimal(float)`` is the exact value the double represents, so its first
    significant digit is the true leading digit. This is a genuinely different
    mechanism from the integer-ratio scaling in :func:`first_digit`, so the
    comparison is a real cross-check rather than a restatement.

    A ``%e`` format would be the wrong oracle: it *rounds*, so
    ``6.999999999999999999e-304`` reads as a 7. Benford's law is defined on
    truncation.
    """
    return int(Decimal(value).as_tuple().digits[0])


def test_first_digit_is_exact_across_the_whole_magnitude_range() -> None:
    """Sweep the double exponent range against the exact oracle.

    This is the regression test for two defects the obvious implementations
    have: iterative ``*= 10.0`` scaling compounds rounding error (``1e-300``
    drifts to a mantissa of 9.999999999999993 and reports 9 instead of 1), and
    a ``.17e`` format rounds the mantissa across a power-of-ten boundary. Both
    are silent — they return a plausible digit, not an error — so only a sweep
    of this width catches them.
    """
    mantissas = (1.0, 1.0000000000000002, 3.0, 4.5, 7.0, 9.0, 9.999999999999998)
    checked = 0
    for exponent in range(-320, 301):
        for mantissa in mantissas:
            value = mantissa * (10.0**exponent)
            if value <= 0.0 or math.isinf(value):
                continue
            digit = ba.first_digit(value)
            assert 1 <= digit <= 9, f"{value!r} produced digit {digit}"
            assert digit == _exact_leading_digit(value), f"{value!r}"
            checked += 1
    assert checked > 3000, "the sweep must actually cover the magnitude range"


def test_first_digit_is_exact_on_binary_scaled_and_subnormal_values() -> None:
    """Binary-scaled and subnormal magnitudes (no short decimal form) also agree."""
    checked = 0
    for exponent in range(-1070, 1021, 7):
        for fraction in (0.5, 0.625, 0.8125, 0.9999999999999999):
            value = math.ldexp(fraction, exponent)
            if value <= 0.0 or math.isinf(value):
                continue
            assert ba.first_digit(value) == _exact_leading_digit(value), f"{value!r}"
            checked += 1
    assert checked > 500
    # Smallest positive subnormal is 4.94...e-324 — leading digit 4, not 5.
    assert ba.first_digit(5e-324) == 4


def test_first_digit_rejects_the_iterative_scaling_answer() -> None:
    """Pin the specific value the old drifting implementation got wrong."""
    drifting = abs(1e-300)
    while drifting >= 10.0:
        drifting /= 10.0
    while drifting < 1.0:
        drifting *= 10.0
    assert int(drifting) == 9, "the naive scaling really does drift here"
    assert ba.first_digit(1e-300) == 1


def test_critical_value_metadata_is_self_consistent() -> None:
    """The reported df/alpha must describe the critical value actually applied."""
    assert ba.BENFORD_DEGREES_OF_FREEDOM == 8  # nine digit classes minus one
    assert ba.BENFORD_ALPHA == 0.05
    report = ba.benford_report(ba.canonical_ledger_amounts())
    assert report.critical_value == ba.BENFORD_CRITICAL_VALUE_05
    assert report.conforms is (report.chi_square <= ba.BENFORD_CRITICAL_VALUE_05)


def test_canonical_ledger_docstring_count_matches_the_data() -> None:
    """The ledger's stated composition (40 natural + 61 round) must be the real one."""
    amounts = ba.canonical_ledger_amounts()
    assert len(amounts) == 101
    round_deposits = [a for a in amounts if a >= 10000.0]
    assert len(round_deposits) == 61
    assert len(amounts) - len(round_deposits) == 40
