"""AgriShield AI - Geographic & Routing Utilities

Implements accurate Haversine distance calculations and rural transport cost heuristics.
"""

import math
from typing import Tuple


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth in kilometers."""
    R = 6371.0  # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def estimate_transport_cost_inr(
    distance_km: float,
    weight_kg: float,
    requires_cold_chain: bool = False,
    base_rate_per_km: float = 25.0,
) -> float:
    """Estimate rural transportation cost in INR.

    Accounts for road winding factor (1.25x haversine), tonnage factor, and refrigeration.
    """
    # Road routing in rural India is typically 1.25 - 1.3x straight-line distance
    road_distance_km = distance_km * 1.25
    tonnes = max(0.5, weight_kg / 1000.0)

    # Base cost: base rate per km scaled by weight
    cost = road_distance_km * base_rate_per_km * (1.0 + (tonnes - 1.0) * 0.15)

    # Refrigeration surcharge (30-40% increase for power & compressor running)
    if requires_cold_chain:
        cost *= 1.35

    # Minimum dispatch charge for rural pickup
    cost = max(cost, 500.0)
    return round(cost, 2)

