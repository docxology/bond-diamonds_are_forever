"""Space-mirror orbital weapon targeting geometry.

CONFLICT STONE models the orbital weapon of the film: a satellite whose mirror
focuses sunlight to vaporize a ground target. This module solves the geometry
that governs a strike:

* **line-of-sight / occultation** — is the target on the visible hemisphere,
  or does the beam ray dip below the Earth's surface before reaching it?
* **slant range** — the straight-line distance the beam must travel.
* **pointing / elevation** — the angle above the target's local horizon, used
  for beam steering and horizon-limit checks.
* **beam delivery** — captured solar power scaled by mirror area and the
  irradiance implied for a focused spot.

Deterministic vector math (stdlib ``math`` only); no RNG.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "EARTH_RADIUS_KM",
    "SOLAR_CONSTANT_W_M2",
    "GroundTarget",
    "Satellite",
    "beam_power_w",
    "canonical_satellite",
    "canonical_targets",
    "elevation_angle_deg",
    "irradiance_at_target",
    "is_visible",
    "satellite_position",
    "slant_range_km",
    "target_position",
    "to_cartesian",
]

#: Mean Earth radius used for the targeting sphere (km).
EARTH_RADIUS_KM = 6371.0
#: Standard solar irradiance at 1 AU (W/m^2).
SOLAR_CONSTANT_W_M2 = 1361.0

_Vec3 = tuple[float, float, float]


@dataclass(frozen=True)
class GroundTarget:
    """A city / ground location to be targeted, geodetic coordinates in degrees."""

    name: str
    lat_deg: float
    lon_deg: float

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("GroundTarget.name must be a non-empty string")
        if not isinstance(self.lat_deg, (int, float)) or isinstance(self.lat_deg, bool):
            raise TypeError("GroundTarget.lat_deg must be a non-boolean number")
        if not isinstance(self.lon_deg, (int, float)) or isinstance(self.lon_deg, bool):
            raise TypeError("GroundTarget.lon_deg must be a non-boolean number")
        if not -90.0 <= self.lat_deg <= 90.0:
            raise ValueError("GroundTarget.lat_deg must be within [-90, 90]")
        if not -180.0 <= self.lon_deg <= 180.0:
            raise ValueError("GroundTarget.lon_deg must be within [-180, 180]")


@dataclass(frozen=True)
class Satellite:
    """An orbital mirror above a sub-satellite point at a fixed altitude (km)."""

    altitude_km: float
    lat_deg: float
    lon_deg: float

    def __post_init__(self) -> None:
        if not isinstance(self.altitude_km, (int, float)) or isinstance(self.altitude_km, bool):
            raise TypeError("Satellite.altitude_km must be a non-boolean number")
        if self.altitude_km < 0:
            raise ValueError("Satellite.altitude_km cannot be negative")
        if not -90.0 <= self.lat_deg <= 90.0:
            raise ValueError("Satellite.lat_deg must be within [-90, 90]")
        if not -180.0 <= self.lon_deg <= 180.0:
            raise ValueError("Satellite.lon_deg must be within [-180, 180]")

    def position(self) -> _Vec3:
        """Geocentric cartesian position of the mirror above the sub-satellite point."""
        return to_cartesian(self.lat_deg, self.lon_deg, EARTH_RADIUS_KM + self.altitude_km)


def _dot(left: _Vec3, right: _Vec3) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def _norm(vector: _Vec3) -> float:
    return math.sqrt(_dot(vector, vector))


def to_cartesian(lat_deg: float, lon_deg: float, radius_km: float) -> _Vec3:
    """Convert geodetic (lat, lon, radius) to geocentric cartesian (x, y, z)."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    cos_lat = math.cos(lat)
    return (
        radius_km * cos_lat * math.cos(lon),
        radius_km * cos_lat * math.sin(lon),
        radius_km * math.sin(lat),
    )


def target_position(target: GroundTarget, radius_km: float = EARTH_RADIUS_KM) -> _Vec3:
    """Geocentric cartesian position of a ground target on the Earth's surface."""
    return to_cartesian(target.lat_deg, target.lon_deg, radius_km)


def satellite_position(satellite: Satellite) -> _Vec3:
    """Geocentric cartesian position of a satellite (convenience wrapper)."""
    return satellite.position()


def _closest_distance_to_origin(start: _Vec3, end: _Vec3) -> float:
    """Distance from the Earth's centre to the nearest point on ``start->end``."""
    delta = (end[0] - start[0], end[1] - start[1], end[2] - start[2])
    denom = _dot(delta, delta)
    if denom == 0.0:
        return _norm(start)
    parameter = -_dot(start, delta) / denom
    parameter = max(0.0, min(1.0, parameter))
    closest = (
        start[0] + parameter * delta[0],
        start[1] + parameter * delta[1],
        start[2] + parameter * delta[2],
    )
    return _norm(closest)


def is_visible(
    satellite: Satellite,
    target: GroundTarget,
    radius_km: float = EARTH_RADIUS_KM,
    tolerance_km: float = 1.0,
) -> bool:
    """True when the beam ray to ``target`` is not occulted by the Earth.

    The target sits on the surface (distance == ``radius_km``). If the closest
    point of the satellite->target ray dips more than ``tolerance_km`` inside
    the sphere, the target is behind the limb and the beam cannot reach it.
    """
    start = satellite.position()
    end = target_position(target, radius_km)
    closest = _closest_distance_to_origin(start, end)
    return closest >= radius_km - tolerance_km


def slant_range_km(satellite: Satellite, target: GroundTarget) -> float:
    """Straight-line distance from mirror to target (km)."""
    sat = satellite.position()
    tgt = target_position(target)
    return _norm((sat[0] - tgt[0], sat[1] - tgt[1], sat[2] - tgt[2]))


def elevation_angle_deg(satellite: Satellite, target: GroundTarget) -> float:
    """Angle of the mirror above the target's local horizon, in degrees.

    A value <= 0 means the mirror is below the target's horizon (not visible).
    """
    sat = satellite.position()
    tgt = target_position(target)
    tgt_len = _norm(tgt)
    up = (tgt[0] / tgt_len, tgt[1] / tgt_len, tgt[2] / tgt_len)
    relative = (sat[0] - tgt[0], sat[1] - tgt[1], sat[2] - tgt[2])
    rel_len = _norm(relative)
    if rel_len == 0.0:
        return 90.0
    sin_elevation = _dot(relative, up) / rel_len
    return math.degrees(math.asin(max(-1.0, min(1.0, sin_elevation))))


def beam_power_w(mirror_area_m2: float) -> float:
    """Solar power one mirror of ``mirror_area_m2`` captures at 1 AU (watts).

    Raises:
        ValueError: if ``mirror_area_m2`` is negative (a negative aperture
            would silently produce negative power downstream).
    """
    if mirror_area_m2 < 0:
        raise ValueError("mirror_area_m2 cannot be negative")
    return SOLAR_CONSTANT_W_M2 * mirror_area_m2


def irradiance_at_target(mirror_area_m2: float, spot_radius_m: float) -> float:
    """Mean irradiance (W/m^2) delivered to a focal spot of the given radius.

    The mirror's full captured power is assumed focused onto one circular
    ``spot_radius_m`` target, so the delivered flux scales inversely with the
    square of the spot radius.

    Raises:
        ValueError: if ``spot_radius_m`` is not positive or the mirror area is
            negative.
    """
    if spot_radius_m <= 0:
        raise ValueError("spot_radius_m must be positive")
    spot_area = math.pi * spot_radius_m * spot_radius_m
    return beam_power_w(mirror_area_m2) / spot_area


def canonical_satellite() -> Satellite:
    """The canonical CONFLICT STONE mirror: geostationary over Las Vegas."""
    return Satellite(altitude_km=36000.0, lat_deg=36.17, lon_deg=-115.14)


def canonical_targets() -> tuple[GroundTarget, ...]:
    """The canonical threatened cities: two on the mirror's visible face, one behind it."""
    return (
        GroundTarget("Las Vegas", 36.17, -115.14),
        GroundTarget("Washington DC", 38.90, -77.04),
        GroundTarget("Beijing", 39.90, 116.41),
    )
