"""Tests for diamond-lot weight & density reconciliation forensics."""

from __future__ import annotations

import pytest

from diamonds_are_forever.lot_forensics import (
    CANONICAL_LOT_ID,
    CUTTING_LOSS_LIMIT,
    DENSITY_MAX_G_CM3,
    DENSITY_MIN_G_CM3,
    DIAMOND_DENSITY_G_CM3,
    HandoffSample,
    LotForensicError,
    audit_lot,
    canonical_lot_samples,
)

D = 3.52  # nominal diamond density


def _sample(
    weight_in: float,
    weight_out: float,
    density: float = D,
    *,
    frm: str = "a",
    to: str = "b",
    lot: str = "L",
) -> HandoffSample:
    return HandoffSample(lot, frm, to, weight_in, weight_out, measured_density_g_cm3=density)


# ---------------------------------------------------------------- canonical


def test_canonical_lot_is_flagrant() -> None:
    report = audit_lot(canonical_lot_samples())
    assert len(report.samples) == 5
    assert len(report.anomalies) == 2
    assert report.score == 4
    assert report.verdict == "flagrant"
    codes = [code for _i, code, _d in report.anomalies]
    assert "density_mismatch" in codes
    assert "excessive_loss" in codes


def test_canonical_flags_land_on_the_swap_and_theft() -> None:
    report = audit_lot(canonical_lot_samples())
    indices = {index for index, _code, _detail in report.anomalies}
    assert indices == {3, 4}
    assert report.flags[3] == "density_mismatch"
    assert report.flags[4] == "excessive_loss"


# ----------------------------------------------------------- rule branches


def test_clean_lot_no_anomalies() -> None:
    report = audit_lot((_sample(10.0, 8.0), _sample(8.0, 8.0)))
    assert report.anomalies == ()
    assert report.score == 0
    assert report.verdict == "clean"


def test_density_mismatch_is_suspicious() -> None:
    report = audit_lot((_sample(10.0, 10.0, density=2.5),))
    assert len(report.anomalies) == 1
    assert report.anomalies[0][1] == "density_mismatch"
    assert report.score == 3
    assert report.verdict == "suspicious"


def test_weight_gain_is_flagged() -> None:
    report = audit_lot((_sample(10.0, 12.0),))
    assert report.anomalies[0][1] == "weight_gain"
    assert report.score == 2
    assert report.verdict == "suspicious"


def test_excessive_loss_is_suspicious() -> None:
    report = audit_lot((_sample(10.0, 2.0),))
    assert report.anomalies[0][1] == "excessive_loss"
    assert report.score == 1
    assert report.verdict == "suspicious"


def test_combined_weight_loss_and_density_flag() -> None:
    report = audit_lot((_sample(10.0, 2.0, density=2.5),))
    assert "excessive_loss;density_mismatch" in report.flags
    assert len(report.anomalies) == 2
    assert report.verdict == "flagrant"


def test_loss_within_allowance_not_flagged() -> None:
    # 2.5 g loss on a 10 g lot is exactly 25% — allowed, not beyond.
    report = audit_lot((_sample(10.0, 7.5),))
    assert report.anomalies == ()


def test_loss_just_beyond_allowance_flagged() -> None:
    report = audit_lot((_sample(10.0, 7.49),))
    assert report.anomalies and report.anomalies[0][1] == "excessive_loss"


def test_custom_cutting_alliance_lowers_threshold() -> None:
    report = audit_lot((_sample(10.0, 8.0),), cutting_loss_limit=0.10)
    assert len(report.anomalies) == 1


def test_determinism() -> None:
    assert audit_lot(canonical_lot_samples()) == audit_lot(canonical_lot_samples())


# ------------------------------------------------------------------- input


def test_handoff_sample_rejects_empty_lot() -> None:
    with pytest.raises(ValueError):
        HandoffSample("", "a", "b", 1.0, 1.0)


def test_handoff_sample_rejects_empty_actor() -> None:
    with pytest.raises(ValueError):
        HandoffSample("L", "", "b", 1.0, 1.0)


def test_handoff_sample_rejects_negative_weight() -> None:
    with pytest.raises(ValueError):
        HandoffSample("L", "a", "b", -1.0, 1.0)


def test_handoff_sample_rejects_non_number_weight() -> None:
    with pytest.raises(TypeError):
        HandoffSample("L", "a", "b", "heavy", 1.0)  # type: ignore[arg-type]


def test_handoff_sample_rejects_non_positive_density() -> None:
    with pytest.raises(ValueError):
        HandoffSample("L", "a", "b", 1.0, 1.0, measured_density_g_cm3=0.0)


def test_audit_empty_samples() -> None:
    with pytest.raises(LotForensicError):
        audit_lot(())


def test_audit_rejects_non_sequence() -> None:
    with pytest.raises(TypeError):
        audit_lot(123)  # type: ignore[arg-type]


def test_audit_rejects_non_sample_entry() -> None:
    with pytest.raises(TypeError):
        audit_lot([_sample(1.0, 1.0), "not-a-sample"])  # type: ignore[list-item]


def test_audit_rejects_negative_cutting_limit() -> None:
    with pytest.raises(LotForensicError):
        audit_lot((_sample(1.0, 1.0),), cutting_loss_limit=-0.1)


def test_audit_rejects_inverted_density_window() -> None:
    with pytest.raises(LotForensicError):
        audit_lot((_sample(1.0, 1.0),), density_min=3.8, density_max=3.4)


def test_sample_rejects_a_non_numeric_density() -> None:
    with pytest.raises(TypeError, match="measured_density_g_cm3"):
        HandoffSample("L", "a", "b", 1.0, 1.0, measured_density_g_cm3="heavy")  # type: ignore[arg-type]


def test_audit_defaults_are_the_published_module_constants() -> None:
    """The manuscript cites these thresholds; the defaults must be them."""
    assert CUTTING_LOSS_LIMIT == 0.25
    assert DENSITY_MIN_G_CM3 < DIAMOND_DENSITY_G_CM3 < DENSITY_MAX_G_CM3
    # A loss exactly at the allowance is legitimate; a hair beyond it is not.
    at_limit = audit_lot([_sample(10.0, 10.0 - 10.0 * CUTTING_LOSS_LIMIT)])
    assert at_limit.verdict == "clean"
    beyond = audit_lot([_sample(10.0, 10.0 - 10.0 * CUTTING_LOSS_LIMIT - 0.01)])
    assert beyond.anomalies[0][1] == "excessive_loss"


def test_canonical_samples_all_carry_the_published_lot_id() -> None:
    assert {s.lot for s in canonical_lot_samples()} == {CANONICAL_LOT_ID}
