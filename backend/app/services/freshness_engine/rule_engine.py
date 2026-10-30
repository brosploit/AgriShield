"""AgriShield AI - Rule-Based Freshness Intelligence Engine

Calculates deterioration risk score (0-100), risk classification, estimated urgency,
recommended action, and explainable influencing factors based on biological crop parameters.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.services.freshness_engine.crop_rules import get_crop_profile


class RuleBasedFreshnessEngine:
    """Agricultural deterioration assessment based on respiration rates, temperature stress,

    relative humidity deficit, and storage conditions.
    """

    def __init__(self, model_version: str = "1.0.0-rule-calibrated"):
        self.model_version = model_version

    def assess(
        self,
        crop_name: str,
        harvest_datetime: datetime,
        current_temp_c: float,
        current_humidity_pct: float,
        storage_type: str,
        storage_duration_hours: float,
        transportation_conditions: str = "ambient_open",
        crop_quantity_kg: float = 100.0,
        sensor_readings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        profile = get_crop_profile(crop_name)
        influencing_factors = {}

        # 1. Temperature Impact
        temp_score = 0.0
        optimal_min = profile["optimal_temp_min_c"]
        optimal_max = profile["optimal_temp_max_c"]
        chilling_thresh = profile["chilling_injury_threshold_c"]
        heat_thresh = profile["heat_stress_threshold_c"]
        q10 = profile["q10_factor"]

        if optimal_min <= current_temp_c <= optimal_max:
            temp_score = 5.0  # Optimal range
            influencing_factors["temperature"] = "Optimal holding temperature maintained."
        elif current_temp_c > optimal_max:
            excess = current_temp_c - optimal_max
            # Exponential acceleration per Q10 factor
            temp_score = min(45.0, 10.0 + (excess * 2.5 * (q10 / 1.5)))
            if current_temp_c >= heat_thresh:
                temp_score = min(50.0, temp_score + 10.0)
                influencing_factors["temperature"] = (
                    f"Severe heat stress: {current_temp_c}°C exceeds heat threshold of {heat_thresh}°C."
                )
            else:
                influencing_factors["temperature"] = (
                    f"Elevated temperature: {current_temp_c}°C is {round(excess, 1)}°C above optimal maximum ({optimal_max}°C)."
                )
        elif current_temp_c < chilling_thresh:
            temp_score = 35.0
            influencing_factors["temperature"] = (
                f"Chilling injury risk: {current_temp_c}°C is below safe minimum ({chilling_thresh}°C)."
            )
        else:
            temp_score = 15.0
            influencing_factors["temperature"] = (
                f"Cool ambient temperature ({current_temp_c}°C) is acceptable but below optimal comfort ({optimal_min}°C)."
            )

        # 2. Relative Humidity Impact
        hum_score = 0.0
        hum_min = profile["optimal_humidity_min_pct"]
        hum_max = profile["optimal_humidity_max_pct"]

        if hum_min <= current_humidity_pct <= hum_max:
            hum_score = 5.0
            influencing_factors["humidity"] = "Relative humidity within safe physiological range."
        elif current_humidity_pct < hum_min:
            deficit = hum_min - current_humidity_pct
            hum_score = min(30.0, 10.0 + (deficit * 0.75))
            influencing_factors["humidity"] = (
                f"Desiccation / wilting risk: {current_humidity_pct}% is below optimal minimum of {hum_min}%."
            )
        else:
            excess_hum = current_humidity_pct - hum_max
            hum_score = min(30.0, 10.0 + (excess_hum * 0.8))
            influencing_factors["humidity"] = (
                f"Fungal & condensation risk: {current_humidity_pct}% exceeds optimal maximum of {hum_max}%."
            )

        # 3. Storage Type & Storage Duration Impact
        storage_multiplier = profile.get("storage_multipliers", {}).get(storage_type.lower(), 1.0)
        standard_shelf_life_hours = profile["standard_shelf_life_days"] * 24.0

        # Effective age ratio
        effective_age_ratio = (storage_duration_hours * storage_multiplier) / standard_shelf_life_hours
        storage_score = min(35.0, effective_age_ratio * 35.0)

        influencing_factors["storage"] = (
            f"Storage in '{storage_type}' (multiplier {storage_multiplier}x) for {round(storage_duration_hours, 1)} hrs "
            f"against baseline shelf life of {profile['standard_shelf_life_days']} days."
        )

        # 4. Transportation Conditions Impact
        transport_score = 0.0
        tc = transportation_conditions.lower()
        if "refrigerated" in tc:
            transport_score = -5.0
            influencing_factors["transportation"] = "Active cold chain significantly slows metabolic decay."
        elif "ventilated" in tc:
            transport_score = 2.0
            influencing_factors["transportation"] = "Ventilated transport prevents heat and moisture entrapment."
        elif "covered" in tc:
            transport_score = 7.0
            influencing_factors["transportation"] = "Covered transport protects against direct sun and dust."
        else:  # ambient_open
            transport_score = 15.0
            influencing_factors["transportation"] = "Open ambient transport exposes produce to sun, dust, and rapid drying."

        # 5. Optional Sensor Telemetry
        sensor_score = 0.0
        if sensor_readings:
            influencing_factors["sensor_readings"] = sensor_readings
            if sensor_readings.get("ethylene_ppm", 0) > 1.0 and profile.get("ethylene_sensitivity") in ["high", "very_high"]:
                sensor_score += 10.0
                influencing_factors["sensors"] = "Elevated ethylene gas detected; ripening accelerated."
            if sensor_readings.get("internal_hotspot_detected", False):
                sensor_score += 15.0
                influencing_factors["sensors"] = "Biomass heating detected inside storage stack."

        # Compute Raw Deterioration Risk Score (0 - 100)
        raw_score = temp_score + hum_score + storage_score + transport_score + sensor_score
        risk_score = round(max(0.0, min(100.0, raw_score)), 1)

        # Classify Risk Category
        if risk_score <= 25.0:
            risk_category = "Low"
            estimated_urgency = "Storage Safe"
            recommended_action = (
                f"Produce is in fresh condition. Suitable for standard storage or regular marketing window. "
                f"Maintain storage in {storage_type} and conduct periodic quality checks."
            )
        elif risk_score <= 50.0:
            risk_category = "Moderate"
            estimated_urgency = "Normal Marketing (3-5 Days)"
            recommended_action = (
                f"Mild deterioration indicators observed. Prioritize listing for sale in the marketplace or "
                f"transferring to improved storage (ventilated godown or cold room) within 72 hours."
            )
        elif risk_score <= 75.0:
            risk_category = "High"
            estimated_urgency = "Urgent Action Required (24-48 Hours)"
            recommended_action = (
                f"High deterioration risk detected due to {influencing_factors.get('temperature', 'adverse storage')}. "
                f"Aggregate with nearby buyers immediately, consider collective rapid dispatch, or process into value-added products."
            )
        else:
            risk_category = "Critical"
            estimated_urgency = "Immediate Liquidation (<24 Hours)"
            recommended_action = (
                f"Critical post-harvest decay threshold imminent! Immediate local sale, local mandi dispatch, "
                f"or flash-cooling required to prevent catastrophic loss."
            )

        return {
            "risk_score": risk_score,
            "risk_category": risk_category,
            "estimated_urgency": estimated_urgency,
            "recommended_action": recommended_action,
            "influencing_factors": influencing_factors,
            "model_version": self.model_version,
            "confidence_score": 0.92,  # Calibrated rule confidence
            "assessment_timestamp": datetime.now(timezone.utc),
        }

