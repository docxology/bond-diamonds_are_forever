"""Tests for Benford's-law laundering detection (deterministic, no mocks)."""

from __future__ import annotations

import math
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

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
    """A near-Benford count set must land *below the critical value*, not merely low.

    The bound is the critical value the audit actually applies. An earlier
    ``< 20.0`` bound sat above 15.507, so it would have passed a count set the
    audit itself flags as anomalous — it could not distinguish conforming from
    anomalous at all.
    """
    counts = {1: 30, 2: 18, 3: 12, 4: 10, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4}
    assert benford_chi_square(counts) < BENFORD_CRITICAL_VALUE_05


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
    assert report.transactions == 141
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


def test_canonical_ledger_is_exactly_its_two_documented_halves() -> None:
    """The ledger's stated composition must be the real one, in order."""
    legitimate = ba.legitimate_ledger_amounts()
    laundered = ba.laundered_deposit_amounts()
    assert len(legitimate) == ba.LEGITIMATE_LEDGER_SIZE == 80
    assert len(laundered) == 61
    assert ba.canonical_ledger_amounts() == legitimate + laundered


# ------------------------------------------------- negative control (specificity)


def test_legitimate_baseline_conforms_the_negative_control() -> None:
    """THE NEGATIVE CONTROL: the audit must *not* fire on the legitimate half.

    Without this the package would only ever have shown the test firing, which
    is equally consistent with a test that fires on every ledger. This
    assertion is what makes the anomalous verdict on the full ledger mean
    something.
    """
    report = benford_report(ba.legitimate_ledger_amounts())
    assert report.transactions == ba.LEGITIMATE_LEDGER_SIZE
    assert report.chi_square < BENFORD_CRITICAL_VALUE_05
    assert report.conforms is True


def test_legitimate_baseline_leading_digits_are_the_fibonacci_digits() -> None:
    """Bind the baseline to the theorem it rests on, via an independent oracle.

    Benford conformance here is a property of the Fibonacci sequence (log10 of
    its terms is an irrational rotation, equidistributed mod 1), not of any
    digit frequency chosen by hand. This recomputes the sequence independently
    of the module and checks digit-for-digit that the ledger amounts really do
    carry those leading digits — so the baseline cannot be quietly retuned
    into conformance without breaking the stated provenance.
    """
    previous, current = 1, 1
    for _ in range(16):  # skip to the first four-significant-digit term
        previous, current = current, previous + current
    amounts = ba.legitimate_ledger_amounts()
    assert len(amounts) == ba.LEGITIMATE_LEDGER_SIZE
    for amount in amounts:
        assert first_digit(amount) == int(str(previous)[0]), f"{amount!r} vs F={previous}"
        previous, current = current, previous + current


def test_legitimate_baseline_spans_several_decades() -> None:
    """A single-decade baseline is a weaker control; assert the spread is real."""
    amounts = ba.legitimate_ledger_amounts()
    decades = {math.floor(math.log10(a)) for a in amounts}
    assert len(decades) >= 3
    assert min(amounts) < 1_000.0 < max(amounts)


# ------------------------------------------------- positive case + discrimination


def test_laundered_deposits_alone_are_anomalous() -> None:
    """The positive case: round-figure structuring collapses onto 1, 2 and 5."""
    report = benford_report(ba.laundered_deposit_amounts())
    assert report.chi_square > BENFORD_CRITICAL_VALUE_05
    assert report.conforms is False
    assert {d for d, n in report.distribution.items() if n} == {"1", "2", "5"}


def test_audit_discriminates_the_two_halves() -> None:
    """The verdict must flip when — and only when — the laundered cash is added.

    Conforming baseline, anomalous full ledger, from the same code path: the
    audit separates the halves rather than rejecting everything put to it.
    """
    clean = benford_report(ba.legitimate_ledger_amounts())
    dirty = benford_report(ba.canonical_ledger_amounts())
    assert clean.conforms is True
    assert dirty.conforms is False
    assert dirty.chi_square > BENFORD_CRITICAL_VALUE_05 > clean.chi_square


# --------------------------------------------------------- digit contributions


def test_digit_contributions_sum_to_the_chi_square() -> None:
    counts = {1: 46, 2: 34, 3: 9, 4: 9, 5: 26, 6: 5, 7: 5, 8: 4, 9: 3}
    contributions = ba.digit_contributions(counts)
    assert set(contributions) == set(range(1, 10))
    assert sum(contributions.values()) == pytest.approx(benford_chi_square(counts))


def test_digit_contributions_empty_is_all_zero() -> None:
    assert ba.digit_contributions({}) == dict.fromkeys(range(1, 10), 0.0)


def test_digit_contributions_rejects_non_mapping() -> None:
    with pytest.raises(TypeError):
        ba.digit_contributions([1, 2, 3])  # type: ignore[arg-type]


def test_claim_ledger_benford_entries_match_live_computation() -> None:
    """The registered benford.* claims must equal what the core actually returns.

    ``data/claim_ledger.yaml`` says every headline number traces to a live
    computation. That is only true if something checks it, so this recomputes
    each benford claim from the core and compares.
    """
    ledger_path = Path(__file__).resolve().parents[1] / "data" / "claim_ledger.yaml"
    claims = {
        claim["id"]: claim["value"]
        for claim in yaml.safe_load(ledger_path.read_text(encoding="utf-8"))["claims"]
    }
    full = benford_report(ba.canonical_ledger_amounts())
    legitimate = benford_report(ba.legitimate_ledger_amounts())
    assert claims["benford.transactions"] == full.transactions
    assert claims["benford.chi_square"] == pytest.approx(full.chi_square)
    assert claims["benford.verdict"] == ("conforms" if full.conforms else "anomalous")
    assert claims["benford.legitimate_transactions"] == legitimate.transactions
    assert claims["benford.legitimate_chi_square"] == pytest.approx(legitimate.chi_square)
    assert claims["benford.legitimate_verdict"] == (
        "conforms" if legitimate.conforms else "anomalous"
    )


def test_round_figure_deposits_dominate_the_canonical_statistic() -> None:
    """The digit the manuscript names as the carrier is derived, not asserted."""
    counts = {
        int(d): n for d, n in benford_report(ba.canonical_ledger_amounts()).distribution.items()
    }
    contributions = ba.digit_contributions(counts)
    carrier = max(contributions, key=lambda digit: contributions[digit])
    assert carrier == 5  # 5 x 10^n structuring
    assert contributions[carrier] > 0.5 * sum(contributions.values())
    # The manuscript states the ledger runs above Benford on exactly 1, 2 and 5
    # — the digits the round-figure deposits sit on — and below it elsewhere.
    total = sum(counts.values())
    excess = {
        digit
        for digit in range(1, 10)
        if counts[digit] > total * ba.expected_benford_frequency(digit)
    }
    assert excess == {1, 2, 5}
