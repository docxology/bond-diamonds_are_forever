"""Tests for Benford's-law laundering detection (deterministic, no mocks)."""

from __future__ import annotations

import math

import pytest

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
