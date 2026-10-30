"""AgriShield AI - Agricultural Crop Baseline Guidelines

Provides scientifically referenced baseline thresholds for major Indian crops:
Tomatoes, Onions, Potatoes, Wheat, Paddy Rice, Soybean, Banana, and Mango.
"""

from typing import Dict, Any

CROP_PROFILES: Dict[str, Dict[str, Any]] = {
    "tomato": {
        "name": "Tomato",
        "category": "perishable_vegetable",
        "standard_shelf_life_days": 10.0,
        "optimal_temp_min_c": 13.0,
        "optimal_temp_max_c": 18.0,
        "optimal_humidity_min_pct": 85.0,
        "optimal_humidity_max_pct": 95.0,
        "chilling_injury_threshold_c": 10.0,
        "heat_stress_threshold_c": 30.0,
        "respiration_rate": "high",
        "q10_factor": 2.2,  # Respiration doubles every 10C rise
        "moisture_loss_susceptibility": "high",
        "ethylene_sensitivity": "high",
        "storage_multipliers": {
            "cold_storage": 0.25,
            "ventilated_godown": 0.70,
            "traditional_shed": 1.10,
            "open_air": 1.50,
        },
    },
    "onion": {
        "name": "Onion",
        "category": "perishable_vegetable",
        "standard_shelf_life_days": 120.0,
        "optimal_temp_min_c": 0.0,
        "optimal_temp_max_c": 25.0,
        "optimal_humidity_min_pct": 65.0,
        "optimal_humidity_max_pct": 75.0,
        "chilling_injury_threshold_c": -1.0,
        "heat_stress_threshold_c": 35.0,
        "respiration_rate": "low",
        "q10_factor": 1.6,
        "moisture_loss_susceptibility": "medium",
        "ethylene_sensitivity": "low",
        "storage_multipliers": {
            "cold_storage": 0.20,
            "ventilated_godown": 0.50,
            "traditional_shed": 0.90,
            "open_air": 1.40,
        },
    },
    "potato": {
        "name": "Potato",
        "category": "perishable_vegetable",
        "standard_shelf_life_days": 90.0,
        "optimal_temp_min_c": 7.0,
        "optimal_temp_max_c": 10.0,
        "optimal_humidity_min_pct": 90.0,
        "optimal_humidity_max_pct": 95.0,
        "chilling_injury_threshold_c": 4.0,
        "heat_stress_threshold_c": 28.0,
        "respiration_rate": "low",
        "q10_factor": 1.8,
        "moisture_loss_susceptibility": "medium",
        "ethylene_sensitivity": "medium",
        "storage_multipliers": {
            "cold_storage": 0.20,
            "ventilated_godown": 0.65,
            "traditional_shed": 1.00,
            "open_air": 1.60,
        },
    },
    "wheat": {
        "name": "Wheat",
        "category": "durable_grain",
        "standard_shelf_life_days": 365.0,
        "optimal_temp_min_c": 10.0,
        "optimal_temp_max_c": 24.0,
        "optimal_humidity_min_pct": 50.0,
        "optimal_humidity_max_pct": 65.0,
        "chilling_injury_threshold_c": -10.0,
        "heat_stress_threshold_c": 38.0,
        "respiration_rate": "very_low",
        "q10_factor": 1.2,
        "moisture_loss_susceptibility": "low",
        "ethylene_sensitivity": "none",
        "safe_grain_moisture_pct": 12.0,
        "storage_multipliers": {
            "hermetic_silo": 0.15,
            "grain_silo": 0.25,
            "ventilated_godown": 0.40,
            "traditional_shed": 0.85,
            "open_air": 1.80,
        },
    },
    "rice": {
        "name": "Rice (Paddy)",
        "category": "durable_grain",
        "standard_shelf_life_days": 365.0,
        "optimal_temp_min_c": 12.0,
        "optimal_temp_max_c": 25.0,
        "optimal_humidity_min_pct": 55.0,
        "optimal_humidity_max_pct": 70.0,
        "chilling_injury_threshold_c": -5.0,
        "heat_stress_threshold_c": 36.0,
        "respiration_rate": "very_low",
        "q10_factor": 1.3,
        "moisture_loss_susceptibility": "low",
        "ethylene_sensitivity": "none",
        "safe_grain_moisture_pct": 13.0,
        "storage_multipliers": {
            "hermetic_silo": 0.15,
            "grain_silo": 0.25,
            "ventilated_godown": 0.45,
            "traditional_shed": 0.90,
            "open_air": 1.75,
        },
    },
    "banana": {
        "name": "Banana",
        "category": "perishable_fruit",
        "standard_shelf_life_days": 7.0,
        "optimal_temp_min_c": 13.0,
        "optimal_temp_max_c": 15.0,
        "optimal_humidity_min_pct": 90.0,
        "optimal_humidity_max_pct": 95.0,
        "chilling_injury_threshold_c": 12.0,
        "heat_stress_threshold_c": 32.0,
        "respiration_rate": "very_high",
        "q10_factor": 2.5,
        "moisture_loss_susceptibility": "high",
        "ethylene_sensitivity": "very_high",
        "storage_multipliers": {
            "cold_storage": 0.35,
            "ventilated_godown": 0.85,
            "traditional_shed": 1.25,
            "open_air": 1.65,
        },
    },
    "soybean": {
        "name": "Soybean",
        "category": "oilseed",
        "standard_shelf_life_days": 270.0,
        "optimal_temp_min_c": 10.0,
        "optimal_temp_max_c": 25.0,
        "optimal_humidity_min_pct": 50.0,
        "optimal_humidity_max_pct": 65.0,
        "chilling_injury_threshold_c": -5.0,
        "heat_stress_threshold_c": 35.0,
        "respiration_rate": "low",
        "q10_factor": 1.4,
        "moisture_loss_susceptibility": "medium",
        "ethylene_sensitivity": "none",
        "safe_grain_moisture_pct": 11.0,
        "storage_multipliers": {
            "grain_silo": 0.25,
            "ventilated_godown": 0.45,
            "traditional_shed": 0.90,
            "open_air": 1.70,
        },
    },
}


def get_crop_profile(crop_name: str) -> Dict[str, Any]:
    key = crop_name.strip().lower()
    for profile_key, profile in CROP_PROFILES.items():
        if profile_key in key or key in profile_key:
            return profile

    # Default fallback profile for unspecified produce
    return {
        "name": crop_name,
        "category": "general_produce",
        "standard_shelf_life_days": 14.0,
        "optimal_temp_min_c": 15.0,
        "optimal_temp_max_c": 25.0,
        "optimal_humidity_min_pct": 70.0,
        "optimal_humidity_max_pct": 85.0,
        "chilling_injury_threshold_c": 5.0,
        "heat_stress_threshold_c": 32.0,
        "respiration_rate": "medium",
        "q10_factor": 2.0,
        "moisture_loss_susceptibility": "medium",
        "ethylene_sensitivity": "medium",
        "storage_multipliers": {
            "cold_storage": 0.30,
            "ventilated_godown": 0.70,
            "traditional_shed": 1.00,
            "open_air": 1.50,
        },
    }

