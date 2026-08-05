"""Orbital-mirror beam delivery physics (CONFLICT STONE deepening).

The targeting geometry solves *where* the beam can go; this module solves
*what the beam delivers*. The mirror captures sunlight, focuses it through a
diffraction-limited aperture, and the beam loses energy to atmospheric
attenuation on the way down. The model chains four classic laws:

* **diffraction** — the Airy first-null spot radius ``r = 1.22 * lambda * R / D``
  sets the focused spot size at slant range ``R`` for a mirror of diameter ``D``;
* **Beer–Lambert** — ``T = exp(-k * L)`` gives the atmospheric transmittance
  over path ``L`` at attenuation coefficient ``k``;
* **power budget** — ``P = S * pi*(D/2)^2 * T`` (solar constant x area x
  transmittance), and the delivered irradiance is ``I = P / (pi * r^2)``;
* **vaporization** — a strike needs to deliver a material's vaporization
  fluence, so ``t = F / I`` is the dwell time.

:func:`minimum_mirror_diameter_m` inverts the chain to the mirror size that
delivers a required irradiance at a given range — the honest headline of how
big the weapon must actually be. All values are deterministic; no RNG.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from diamonds_are_forever.orbital_mirror import SOLAR_CONSTANT_W_M2

__all__ = [
    "REQUIRED_STRIKE_IRRADIANCE_W_M2",
    "STEEL_VAPORIZATION_FLUENCE_J_M2",
    "BeamScenario",
    "atmospheric_transmittance",
    "beam_metrics",
    "canonical_beam_scenario",
    "captured_power_w",
    "concentration_factor",
    "delivered_irradiance_w_m2",
    "diffraction_spot_radius_m",
    "minimum_mirror_diameter_m",
    "time_to_vaporize_s",
]

#: Diffraction-limit constant for the Airy first null (1.22).
_AIRY_FIRST_NULL = 1.22
#: Aperture constant in the irradiance inversion (4 * 1.22^2 * pi / pi = 5.9536).
_APERTURE_CONSTANT = 4.0 * _AIRY_FIRST_NULL * _AIRY_FIRST_NULL
#: Steel vaporization fluence used by the canonical strike (J/m^2, ~1 mm layer).
STEEL_VAPORIZATION_FLUENCE_J_M2 = 2.5e8
#: Canonical required strike irradiance (W/m^2).
REQUIRED_STRIKE_IRRADIANCE_W_M2 = 1.0e6


@dataclass(frozen=True)
class BeamScenario:
    """A deterministic beam-delivery scenario for the orbital mirror."""

    mirror_diameter_m: float = 40.0
    wavelength_m: float = 5.0e-7
    slant_range_km: float = 36_998.4  # mirror -> Washington DC at GEO
    attenuation_per_km: float = 0.01
    atmosphere_path_km: float = 80.0

    def __post_init__(self) -> None:
        for label, value in (
            ("mirror_diameter_m", self.mirror_diameter_m),
            ("wavelength_m", self.wavelength_m),
            ("slant_range_km", self.slant_range_km),
            ("attenuation_per_km", self.attenuation_per_km),
            ("atmosphere_path_km", self.atmosphere_path_km),
        ):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"BeamScenario.{label} must be a non-boolean number")
        if self.mirror_diameter_m <= 0:
            raise ValueError("BeamScenario.mirror_diameter_m must be positive")
        if self.wavelength_m <= 0:
            raise ValueError("BeamScenario.wavelength_m must be positive")
        if self.slant_range_km <= 0:
            raise ValueError("BeamScenario.slant_range_km must be positive")
        if self.attenuation_per_km < 0:
            raise ValueError("BeamScenario.attenuation_per_km cannot be negative")
        if self.atmosphere_path_km < 0:
            raise ValueError("BeamScenario.atmosphere_path_km cannot be negative")


def diffraction_spot_radius_m(
    wavelength_m: float, slant_range_m: float, mirror_diameter_m: float
) -> float:
    """Airy first-null spot radius: ``1.22 * lambda * R / D`` (metres)."""
    if wavelength_m <= 0:
        raise ValueError("wavelength_m must be positive")
    if slant_range_m <= 0:
        raise ValueError("slant_range_m must be positive")
    if mirror_diameter_m <= 0:
        raise ValueError("mirror_diameter_m must be positive")
    return float(_AIRY_FIRST_NULL * wavelength_m * slant_range_m / mirror_diameter_m)


def atmospheric_transmittance(attenuation_per_km: float, path_km: float) -> float:
    """Beer-Lambert transmittance ``exp(-k * L)`` along the atmospheric path."""
    if attenuation_per_km < 0:
        raise ValueError("attenuation_per_km cannot be negative")
    if path_km < 0:
        raise ValueError("path_km cannot be negative")
    return float(math.exp(-attenuation_per_km * path_km))


def captured_power_w(mirror_diameter_m: float, transmittance: float = 1.0) -> float:
    """Solar power captured by the mirror aperture, scaled by transmittance."""
    if mirror_diameter_m <= 0:
        raise ValueError("mirror_diameter_m must be positive")
    if not 0.0 < transmittance <= 1.0:
        raise ValueError("transmittance must be within (0, 1]")
    radius = mirror_diameter_m / 2.0
    return float(SOLAR_CONSTANT_W_M2 * math.pi * radius * radius * transmittance)


def delivered_irradiance_w_m2(
    mirror_diameter_m: float,
    wavelength_m: float,
    slant_range_m: float,
    attenuation_per_km: float,
    atmosphere_path_km: float,
) -> float:
    """Delivered irradiance at the focal spot after atmospheric attenuation."""
    spot = diffraction_spot_radius_m(wavelength_m, slant_range_m, mirror_diameter_m)
    transmittance = atmospheric_transmittance(attenuation_per_km, atmosphere_path_km)
    power = captured_power_w(mirror_diameter_m, transmittance)
    return float(power / (math.pi * spot * spot))


def concentration_factor(irradiance_w_m2: float) -> float:
    """Beam concentration over raw sunlight: ``I / S``."""
    if irradiance_w_m2 < 0:
        raise ValueError("irradiance_w_m2 cannot be negative")
    return float(irradiance_w_m2 / SOLAR_CONSTANT_W_M2)


def time_to_vaporize_s(irradiance_w_m2: float, fluence_required_j_m2: float) -> float:
    """Dwell time to deposit ``fluence_required`` at the given irradiance."""
    if irradiance_w_m2 <= 0:
        raise ValueError("irradiance_w_m2 must be positive")
    if fluence_required_j_m2 <= 0:
        raise ValueError("fluence_required_j_m2 must be positive")
    return float(fluence_required_j_m2 / irradiance_w_m2)


def minimum_mirror_diameter_m(
    wavelength_m: float,
    slant_range_m: float,
    required_irradiance_w_m2: float,
    attenuation_per_km: float = 0.0,
    atmosphere_path_km: float = 0.0,
) -> float:
    """Mirror diameter that delivers ``required_irradiance`` at slant range.

    From ``I = S*T*D^4 / (4*1.22^2*lambda^2*R^2)``, solving for ``D``:
    ``D = (I * 4*1.22^2 * lambda^2 * R^2 / (S*T))^(1/4)``.
    """
    if wavelength_m <= 0:
        raise ValueError("wavelength_m must be positive")
    if slant_range_m <= 0:
        raise ValueError("slant_range_m must be positive")
    if required_irradiance_w_m2 <= 0:
        raise ValueError("required_irradiance_w_m2 must be positive")
    transmittance = atmospheric_transmittance(attenuation_per_km, atmosphere_path_km)
    if transmittance <= 0:
        raise ValueError("atmospheric transmittance is zero — the beam cannot reach the target")
    numerator = (
        required_irradiance_w_m2
        * _APERTURE_CONSTANT
        * wavelength_m
        * wavelength_m
        * slant_range_m
        * slant_range_m
    )
    denominator = SOLAR_CONSTANT_W_M2 * transmittance
    return float((numerator / denominator) ** 0.25)


def canonical_beam_scenario() -> BeamScenario:
    """The canonical CONFLICT STONE beam scenario (40 m mirror at GEO)."""
    return BeamScenario()


def beam_metrics(scenario: BeamScenario | None = None) -> dict[str, float]:
    """Compute the canonical beam-delivery metrics for the mission and tokens."""
    scenario = scenario if scenario is not None else canonical_beam_scenario()
    slant_range_m = scenario.slant_range_km * 1000.0
    spot = diffraction_spot_radius_m(
        scenario.wavelength_m, slant_range_m, scenario.mirror_diameter_m
    )
    irradiance = delivered_irradiance_w_m2(
        scenario.mirror_diameter_m,
        scenario.wavelength_m,
        slant_range_m,
        scenario.attenuation_per_km,
        scenario.atmosphere_path_km,
    )
    minimum_diameter = minimum_mirror_diameter_m(
        scenario.wavelength_m,
        slant_range_m,
        REQUIRED_STRIKE_IRRADIANCE_W_M2,
        scenario.attenuation_per_km,
        scenario.atmosphere_path_km,
    )
    return {
        "spot_radius_m": spot,
        "irradiance_w_m2": irradiance,
        "concentration": concentration_factor(irradiance),
        "vaporize_time_s": time_to_vaporize_s(irradiance, STEEL_VAPORIZATION_FLUENCE_J_M2),
        "min_mirror_diameter_m": minimum_diameter,
    }
