"""AgriShield AI - Machine Learning Freshness Engine Interface

Provides a scikit-learn compatible interface for predictive deterioration assessment.
Falls back seamlessly to the calibrated rule-based engine when ML models are absent or uncalibrated.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import os
import joblib

from app.core.config import settings
from app.services.freshness_engine.crop_rules import get_crop_profile
from app.services.freshness_engine.rule_engine import RuleBasedFreshnessEngine


class MLFreshnessEngine:
    """Hybrid ML-rule engine that evaluates trained regression/classification models

    while guaranteeing continuous service availability through rule fallbacks.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(settings.ML_MODEL_PATH, "freshness_model.joblib")
        self.rule_engine = RuleBasedFreshnessEngine(model_version=f"{settings.MODEL_VERSION}-rule")
        self.ml_model = None
        self._load_model()

    def _load_model(self):
        try:
            if Path(self.model_path).exists():
                self.ml_model = joblib.load(self.model_path)
        except Exception:
            self.ml_model = None

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
        """Assess produce deterioration risk."""
        # Baseline rule-based computation provides explainability and robust anchors
        rule_assessment = self.rule_engine.assess(
            crop_name=crop_name,
            harvest_datetime=harvest_datetime,
            current_temp_c=current_temp_c,
            current_humidity_pct=current_humidity_pct,
            storage_type=storage_type,
            storage_duration_hours=storage_duration_hours,
            transportation_conditions=transportation_conditions,
            crop_quantity_kg=crop_quantity_kg,
            sensor_readings=sensor_readings,
        )

        if not self.ml_model:
            # Clean fallback to calibrated agronomic rules
            return rule_assessment

        try:
            profile = get_crop_profile(crop_name)
            opt_temp = (profile["optimal_temp_min_c"] + profile["optimal_temp_max_c"]) / 2.0
            opt_hum = (profile["optimal_humidity_min_pct"] + profile["optimal_humidity_max_pct"]) / 2.0

            # Feature vector
            features = [[
                current_temp_c,
                current_temp_c - opt_temp,
                current_humidity_pct,
                current_humidity_pct - opt_hum,
                storage_duration_hours,
                crop_quantity_kg,
            ]]

            # Predict risk score
            predicted_score = float(self.ml_model.predict(features)[0])
            predicted_score = max(0.0, min(100.0, predicted_score))

            # Blend ML prediction with rule-based safety envelope
            blended_score = round(0.7 * predicted_score + 0.3 * rule_assessment["risk_score"], 1)

            # Re-classify
            if blended_score <= 25.0:
                cat = "Low"
                urgency = "Storage Safe"
            elif blended_score <= 50.0:
                cat = "Moderate"
                urgency = "Normal Marketing (3-5 Days)"
            elif blended_score <= 75.0:
                cat = "High"
                urgency = "Urgent Action Required (24-48 Hours)"
            else:
                cat = "Critical"
                urgency = "Immediate Liquidation (<24 Hours)"

            return {
                "risk_score": blended_score,
                "risk_category": cat,
                "estimated_urgency": urgency,
                "recommended_action": rule_assessment["recommended_action"],
                "influencing_factors": rule_assessment["influencing_factors"],
                "model_version": f"{settings.MODEL_VERSION}-ml-hybrid",
                "confidence_score": 0.88,
                "assessment_timestamp": datetime.now(timezone.utc),
            }
        except Exception:
            return rule_assessment

