from dataclasses import dataclass

from config import (
    ACCESS_FACTORS,
    BASE_KWH_PER_GB,
    GRID_INTENSITY_G_PER_KWH,
    HOPS_ALPHA,
    REFERENCE_HOPS,
)


@dataclass
class ImpactResult:
    total_bytes: int
    total_mb: float
    total_gb: float
    energy_kwh: float
    energy_wh: float
    co2_g: float
    access_factor: float
    hops_factor: float


def compute_transport_impact(
    bytes_up: int,
    bytes_down: int,
    estimated_hops: int,
    access_type: str,
) -> ImpactResult:
    total_bytes = max(0, bytes_up) + max(0, bytes_down)
    total_gb = total_bytes / (1024 ** 3)
    total_mb = total_bytes / (1024 ** 2)

    access_factor = ACCESS_FACTORS.get(access_type, ACCESS_FACTORS["unknown"])

    hops_factor = 1.0 + ((estimated_hops - REFERENCE_HOPS) * HOPS_ALPHA)
    if hops_factor < 0.5:
        hops_factor = 0.5

    energy_kwh = total_gb * BASE_KWH_PER_GB * access_factor * hops_factor
    energy_wh = energy_kwh * 1000.0
    co2_g = energy_kwh * GRID_INTENSITY_G_PER_KWH

    return ImpactResult(
        total_bytes=total_bytes,
        total_mb=total_mb,
        total_gb=total_gb,
        energy_kwh=energy_kwh,
        energy_wh=energy_wh,
        co2_g=co2_g,
        access_factor=access_factor,
        hops_factor=hops_factor,
    )