"""Tests for the orbital-mirror beam delivery physics (deterministic, no mocks)."""

from __future__ import annotations

import math

import pytest

from diamonds_are_forever.beam_physics import (
    REQUIRED_STRIKE_IRRADIANCE_W_M2,
    BeamScenario,
    atmospheric_transmittance,
    beam_metrics,
    canonical_beam_scenario,
    captured_power_w,
    concentration_factor,
    delivered_irradiance_w_m2,
    diffraction_spot_radius_m,
    minimum_mirror_diameter_m,
    time_to_vaporize_s,
)
from diamonds_are_forever.orbital_mirror import SOLAR_CONSTANT_W_M2

# ---------------------------------------------------------------- canonical


def test_canonical_beam_metrics() -> None:
    metrics = beam_metrics()
    assert metrics["spot_radius_m"] == pytest.approx(0.564, abs=1e-2)
    assert metrics["concentration"] == pytest.approx(564.6, rel=0.02)
    assert metrics["vaporize_time_s"] == pytest.approx(325.4, rel=0.02)
    assert metrics["min_mirror_diameter_m"] == pytest.approx(42.7, rel=0.02)
    assert metrics["irradiance_w_m2"] > SOLAR_CONSTANT_W_M2


def test_canonical_scenario_defaults() -> None:
    scenario = canonical_beam_scenario()
    assert scenario.mirror_diameter_m == 40.0
    assert scenario.slant_range_km == pytest.approx(36_998.4)


def test_beam_metrics_deterministic() -> None:
    assert beam_metrics() == beam_metrics()


# ---------------------------------------------------------------- diffraction


def test_diffraction_spot_radius() -> None:
    # r = 1.22 * lambda * R / D
    spot = diffraction_spot_radius_m(5e-7, 1000.0, 10.0)
    assert spot == pytest.approx(1.22 * 5e-7 * 1000.0 / 10.0)


def test_diffraction_bigger_mirror_shrinks_spot() -> None:
    small = diffraction_spot_radius_m(5e-7, 1000.0, 10.0)
    big = diffraction_spot_radius_m(5e-7, 1000.0, 20.0)
    assert big == pytest.approx(small / 2.0)


def test_diffraction_rejects_non_positive_inputs() -> None:
    with pytest.raises(ValueError):
        diffraction_spot_radius_m(0.0, 1000.0, 10.0)
    with pytest.raises(ValueError):
        diffraction_spot_radius_m(5e-7, -1.0, 10.0)
    with pytest.raises(ValueError):
        diffraction_spot_radius_m(5e-7, 1000.0, 0.0)


# ---------------------------------------------------------------- attenuation


def test_atmospheric_transmittance_beer_lambert() -> None:
    assert atmospheric_transmittance(0.01, 80.0) == pytest.approx(math.exp(-0.8))
    assert atmospheric_transmittance(0.0, 100.0) == pytest.approx(1.0)


def test_atmospheric_transmittance_rejects_negative() -> None:
    with pytest.raises(ValueError):
        atmospheric_transmittance(-0.1, 10.0)
    with pytest.raises(ValueError):
        atmospheric_transmittance(0.1, -10.0)


# ---------------------------------------------------------------- power


def test_captured_power_w() -> None:
    # P = S * pi * (D/2)^2
    assert captured_power_w(2.0) == pytest.approx(SOLAR_CONSTANT_W_M2 * math.pi * 1.0)


def test_captured_power_scales_with_transmittance() -> None:
    full = captured_power_w(2.0, 1.0)
    half = captured_power_w(2.0, 0.5)
    assert half == pytest.approx(full / 2.0)


def test_captured_power_rejects_bad_args() -> None:
    with pytest.raises(ValueError):
        captured_power_w(0.0)
    with pytest.raises(ValueError):
        captured_power_w(2.0, transmittance=0.0)
    with pytest.raises(ValueError):
        captured_power_w(2.0, transmittance=1.5)


# ---------------------------------------------------------------- irradiance


def test_delivered_irradiance_positive_and_concentrated() -> None:
    irradiance = delivered_irradiance_w_m2(40.0, 5e-7, 36_998.4 * 1000.0, 0.01, 80.0)
    assert irradiance > SOLAR_CONSTANT_W_M2
    assert concentration_factor(irradiance) == pytest.approx(irradiance / SOLAR_CONSTANT_W_M2)


def test_delivered_irradiance_grows_with_mirror() -> None:
    base = delivered_irradiance_w_m2(30.0, 5e-7, 3.7e7, 0.01, 80.0)
    bigger = delivered_irradiance_w_m2(60.0, 5e-7, 3.7e7, 0.01, 80.0)
    assert bigger > base


def test_concentration_factor_rejects_negative() -> None:
    with pytest.raises(ValueError):
        concentration_factor(-1.0)


# ---------------------------------------------------------------- vaporization


def test_time_to_vaporize() -> None:
    assert time_to_vaporize_s(1_000_000.0, 2.5e8) == pytest.approx(250.0)


def test_time_to_vaporize_rejects_bad_args() -> None:
    with pytest.raises(ValueError):
        time_to_vaporize_s(0.0, 2.5e8)
    with pytest.raises(ValueError):
        time_to_vaporize_s(1.0, 0.0)


# ------------------------------------------------------------- min diameter


def test_minimum_mirror_diameter_inverts_irradiance() -> None:
    # At the solved diameter the delivered irradiance equals the requirement.
    scenario = canonical_beam_scenario()
    slant_range_m = scenario.slant_range_km * 1000.0
    minimum = minimum_mirror_diameter_m(
        scenario.wavelength_m,
        slant_range_m,
        REQUIRED_STRIKE_IRRADIANCE_W_M2,
        scenario.attenuation_per_km,
        scenario.atmosphere_path_km,
    )
    actual = delivered_irradiance_w_m2(
        minimum,
        scenario.wavelength_m,
        slant_range_m,
        scenario.attenuation_per_km,
        scenario.atmosphere_path_km,
    )
    assert actual == pytest.approx(REQUIRED_STRIKE_IRRADIANCE_W_M2, rel=0.02)


def test_minimum_mirror_diameter_increases_with_range() -> None:
    near = minimum_mirror_diameter_m(5e-7, 1.0e6, 1e6)
    far = minimum_mirror_diameter_m(5e-7, 4e7, 1e6)
    assert far > near


def test_minimum_mirror_diameter_rejects_bad_args() -> None:
    with pytest.raises(ValueError):
        minimum_mirror_diameter_m(0.0, 1e7, 1e6)
    with pytest.raises(ValueError):
        minimum_mirror_diameter_m(5e-7, -1.0, 1e6)
    with pytest.raises(ValueError):
        minimum_mirror_diameter_m(5e-7, 1e7, 0.0)


# ---------------------------------------------------------- scenario validation


def test_beam_scenario_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        BeamScenario(mirror_diameter_m=0.0)
    with pytest.raises(ValueError):
        BeamScenario(attenuation_per_km=-1.0)


def test_beam_scenario_rejects_non_number() -> None:
    with pytest.raises(TypeError):
        BeamScenario(mirror_diameter_m="wide")  # type: ignore[arg-type]
