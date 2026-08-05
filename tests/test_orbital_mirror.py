"""Tests for the orbital-mirror targeting geometry (deterministic, no mocks)."""

from __future__ import annotations

import pytest

from diamonds_are_forever.orbital_mirror import (
    EARTH_RADIUS_KM,
    SOLAR_CONSTANT_W_M2,
    GroundTarget,
    Satellite,
    beam_power_w,
    canonical_satellite,
    canonical_targets,
    elevation_angle_deg,
    irradiance_at_target,
    is_visible,
    satellite_position,
    slant_range_km,
    target_position,
    to_cartesian,
)

# ---------------------------------------------------------------- canonical


def test_canonical_mirror_is_geostationary_over_las_vegas() -> None:
    satellite = canonical_satellite()
    assert satellite.altitude_km == pytest.approx(36000.0)
    assert satellite.lat_deg == pytest.approx(36.17)
    assert satellite.lon_deg == pytest.approx(-115.14)


def test_canonical_targets_count() -> None:
    assert len(canonical_targets()) == 3


def test_near_face_targets_visible_far_side_occulted() -> None:
    satellite = canonical_satellite()
    by_name = {target.name: target for target in canonical_targets()}
    assert is_visible(satellite, by_name["Las Vegas"]) is True
    assert is_visible(satellite, by_name["Washington DC"]) is True
    assert is_visible(satellite, by_name["Beijing"]) is False  # behind the limb


def test_sub_satellite_slant_range_equals_altitude() -> None:
    satellite = canonical_satellite()
    las_vegas = GroundTarget("Las Vegas", 36.17, -115.14)
    assert slant_range_km(satellite, las_vegas) == pytest.approx(36000.0)


def test_elevation_above_horizon_for_visible() -> None:
    satellite = canonical_satellite()
    las_vegas = GroundTarget("Las Vegas", 36.17, -115.14)
    assert elevation_angle_deg(satellite, las_vegas) > 70.0


# -------------------------------------------------------------- geometry math


def test_to_cartesian_north_pole() -> None:
    x, y, z = to_cartesian(90.0, 0.0, EARTH_RADIUS_KM)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)
    assert z == pytest.approx(EARTH_RADIUS_KM)


def test_to_cartesian_prime_meridian_equator() -> None:
    x, y, z = to_cartesian(0.0, 0.0, EARTH_RADIUS_KM)
    assert x == pytest.approx(EARTH_RADIUS_KM)
    assert y == pytest.approx(0.0)
    assert z == pytest.approx(0.0)


def test_target_and_satellite_position_wrappers() -> None:
    satellite = canonical_satellite()
    target = canonical_targets()[0]
    sat_pos = satellite_position(satellite)
    tgt_pos = target_position(target)
    assert all(isinstance(v, float) for v in (*sat_pos, *tgt_pos))


def test_slant_range_triangle_inequality() -> None:
    satellite = canonical_satellite()
    target = canonical_targets()[1]  # Washington DC
    rng = slant_range_km(satellite, target)
    assert rng > satellite.altitude_km  # off-nadir range exceeds altitude


def test_beam_power_scales_with_area() -> None:
    assert beam_power_w(1.0) == pytest.approx(SOLAR_CONSTANT_W_M2)
    assert beam_power_w(100.0) == pytest.approx(100.0 * SOLAR_CONSTANT_W_M2)


def test_irradiance_concentration() -> None:
    # Two-fold smaller spot radius -> four-fold higher irradiance.
    wide = irradiance_at_target(10.0, 2.0)
    narrow = irradiance_at_target(10.0, 1.0)
    assert narrow == pytest.approx(4.0 * wide)
    # Focusing onto a 1 m-radius spot concentrates flux above raw sunlight.
    assert narrow > SOLAR_CONSTANT_W_M2


def test_irradiance_rejects_non_positive_spot() -> None:
    with pytest.raises(ValueError):
        irradiance_at_target(10.0, 0.0)


# ------------------------------------------------------- validation branches


def test_ground_target_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        GroundTarget("", 10.0, 10.0)


def test_ground_target_rejects_lat_out_of_range() -> None:
    with pytest.raises(ValueError):
        GroundTarget("x", 91.0, 0.0)


def test_ground_target_rejects_lon_out_of_range() -> None:
    with pytest.raises(ValueError):
        GroundTarget("x", 0.0, 181.0)


def test_ground_target_rejects_non_number_lat() -> None:
    with pytest.raises(TypeError):
        GroundTarget("x", "north", 0.0)  # type: ignore[arg-type]


def test_ground_target_rejects_bool_lon() -> None:
    with pytest.raises(TypeError):
        GroundTarget("x", 0.0, True)  # type: ignore[arg-type]


def test_satellite_rejects_negative_altitude() -> None:
    with pytest.raises(ValueError):
        Satellite(altitude_km=-1.0, lat_deg=0.0, lon_deg=0.0)


def test_satellite_rejects_bool_altitude() -> None:
    with pytest.raises(TypeError):
        Satellite(altitude_km=True, lat_deg=0.0, lon_deg=0.0)  # type: ignore[arg-type]


def test_satellite_rejects_lat_out_of_range() -> None:
    with pytest.raises(ValueError):
        Satellite(altitude_km=100.0, lat_deg=95.0, lon_deg=0.0)


# ------------------------------------------- internal geometry branch coverage


def test_closest_distance_identical_points() -> None:
    # Degenerate segment (start == end) exercises the zero-delta branch.
    satellite = Satellite(altitude_km=0.0, lat_deg=36.17, lon_deg=-115.14)
    las_vegas = GroundTarget("Las Vegas", 36.17, -115.14)
    # start and end coincide -> distance to origin equals the earth radius.
    assert is_visible(satellite, las_vegas) is True  # coincident at surface


def test_elevation_overhead_when_rooted() -> None:
    # A satellite directly above the target reports ~90 deg elevation.
    satellite = Satellite(altitude_km=500.0, lat_deg=36.17, lon_deg=-115.14)
    las_vegas = GroundTarget("Las Vegas", 36.17, -115.14)
    elevation = elevation_angle_deg(satellite, las_vegas)
    assert elevation == pytest.approx(90.0, abs=0.5)


def test_visible_detects_limb_below_surface() -> None:
    # A target geometrically behind the planet is occulted.
    satellite = Satellite(altitude_km=36000.0, lat_deg=36.17, lon_deg=-115.14)
    beijing = GroundTarget("Beijing", 39.90, 116.41)
    assert is_visible(satellite, beijing) is False
    assert slant_range_km(satellite, beijing) > EARTH_RADIUS_KM


def test_math_radians_matrix() -> None:
    # Sanity: a target 90 deg away in latitude has orthogonal position vectors.
    north = to_cartesian(90.0, 0.0, 1.0)
    equator = to_cartesian(0.0, 0.0, 1.0)
    dot = sum(a * b for a, b in zip(north, equator))
    assert dot == pytest.approx(0.0, abs=1e-9)


# ------------------------------------------------- validation & degenerate paths


def test_satellite_rejects_out_of_range_longitude() -> None:
    with pytest.raises(ValueError, match="lon_deg"):
        Satellite(altitude_km=36000.0, lat_deg=0.0, lon_deg=181.0)


def test_elevation_is_ninety_degrees_when_mirror_coincides_with_target() -> None:
    """A zero-length relative vector has no direction — report straight overhead."""
    target = GroundTarget("Zero Altitude", 10.0, 20.0)
    grounded = Satellite(altitude_km=0.0, lat_deg=10.0, lon_deg=20.0)
    assert slant_range_km(grounded, target) == pytest.approx(0.0, abs=1e-9)
    assert elevation_angle_deg(grounded, target) == 90.0


def test_beam_power_rejects_a_negative_aperture() -> None:
    """A negative area would silently yield negative power downstream."""
    with pytest.raises(ValueError, match="cannot be negative"):
        beam_power_w(-1.0)
    with pytest.raises(ValueError, match="cannot be negative"):
        irradiance_at_target(-1.0, 0.5)
    assert beam_power_w(0.0) == 0.0
