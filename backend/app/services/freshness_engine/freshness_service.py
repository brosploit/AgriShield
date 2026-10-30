"""AgriShield AI - Freshness Intelligence Service

Orchestrates assessment requests, interacts with repositories,
and produces explainable post-harvest deterioration analytics.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import EntityNotFoundException
from app.models.crop import Crop, FreshnessAssessment
from app.repositories.crop_repository import CropRepository
from app.schemas.crop import FreshnessAssessmentRequest, FreshnessAssessmentResponse
from app.services.freshness_engine.ml_engine import MLFreshnessEngine
from app.services.freshness_engine.crop_rules import CROP_PROFILES


class FreshnessService:
    def __init__(self, db: Session):
        self.db = db
        self.crop_repo = CropRepository(db)
        self.engine = MLFreshnessEngine()

    def assess_freshness(
        self, request: FreshnessAssessmentRequest, farmer_id: str
    ) -> FreshnessAssessmentResponse:
        # Determine crop
        crop = None
        if request.crop_id:
            crop = self.crop_repo.get_crop_by_id(request.crop_id)
        elif request.crop_name:
            crop = self.crop_repo.get_crop_by_name(request.crop_name)

        crop_name = crop.name if crop else (request.crop_name or "General Crop")
        crop_id = crop.id if crop else None

        if not crop_id:
            # If crop does not exist in DB yet, create a default entry
            new_crop = Crop(
                name=crop_name,
                category="perishable_vegetable" if "tomato" in crop_name.lower() or "onion" in crop_name.lower() else "general_produce",
                standard_shelf_life_days=10.0,
                optimal_temp_min_c=12.0,
                optimal_temp_max_c=22.0,
                optimal_humidity_min_pct=70.0,
                optimal_humidity_max_pct=90.0,
            )
            crop = self.crop_repo.create_crop(new_crop)
            crop_id = crop.id

        # Run assessment calculation
        result = self.engine.assess(
            crop_name=crop_name,
            harvest_datetime=request.harvest_datetime,
            current_temp_c=request.current_temperature_c,
            current_humidity_pct=request.current_humidity_pct,
            storage_type=request.storage_type,
            storage_duration_hours=request.storage_duration_hours,
            transportation_conditions=request.transportation_conditions,
            crop_quantity_kg=request.crop_quantity_kg,
            sensor_readings=request.sensor_readings,
        )

        # Persist record in database
        assessment = FreshnessAssessment(
            farmer_id=farmer_id,
            crop_id=crop_id,
            harvest_datetime=request.harvest_datetime,
            current_temperature_c=request.current_temperature_c,
            current_humidity_pct=request.current_humidity_pct,
            storage_type=request.storage_type,
            storage_duration_hours=request.storage_duration_hours,
            transportation_conditions=request.transportation_conditions,
            crop_quantity_kg=request.crop_quantity_kg,
            sensor_readings_json=request.sensor_readings,
            risk_score=result["risk_score"],
            risk_category=result["risk_category"],
            estimated_urgency=result["estimated_urgency"],
            recommended_action=result["recommended_action"],
            influencing_factors_json=result["influencing_factors"],
            model_version=result["model_version"],
            confidence_score=result.get("confidence_score"),
            assessment_timestamp=result["assessment_timestamp"],
        )

        saved = self.crop_repo.create_freshness_assessment(assessment)

        return FreshnessAssessmentResponse(
            id=saved.id,
            farmer_id=saved.farmer_id,
            crop_id=saved.crop_id,
            crop_name=crop_name,
            risk_score=saved.risk_score,
            risk_category=saved.risk_category,
            estimated_urgency=saved.estimated_urgency,
            recommended_action=saved.recommended_action,
            influencing_factors=saved.influencing_factors_json or {},
            model_version=saved.model_version,
            confidence_score=saved.confidence_score,
            assessment_timestamp=saved.assessment_timestamp,
        )

    def get_history(self, farmer_id: str, limit: int = 50) -> List[FreshnessAssessmentResponse]:
        records = self.crop_repo.get_farmer_assessments(farmer_id, limit=limit)
        return [
            FreshnessAssessmentResponse(
                id=r.id,
                farmer_id=r.farmer_id,
                crop_id=r.crop_id,
                crop_name=r.crop.name if r.crop else "Unknown",
                risk_score=r.risk_score,
                risk_category=r.risk_category,
                estimated_urgency=r.estimated_urgency,
                recommended_action=r.recommended_action,
                influencing_factors=r.influencing_factors_json or {},
                model_version=r.model_version,
                confidence_score=r.confidence_score,
                assessment_timestamp=r.assessment_timestamp,
            )
            for r in records
        ]

    def get_assessment(self, assessment_id: str) -> FreshnessAssessmentResponse:
        record = self.crop_repo.get_assessment_by_id(assessment_id)
        if not record:
            raise EntityNotFoundException("FreshnessAssessment", assessment_id)

        return FreshnessAssessmentResponse(
            id=record.id,
            farmer_id=record.farmer_id,
            crop_id=record.crop_id,
            crop_name=record.crop.name if record.crop else "Unknown",
            risk_score=record.risk_score,
            risk_category=record.risk_category,
            estimated_urgency=record.estimated_urgency,
            recommended_action=record.recommended_action,
            influencing_factors=record.influencing_factors_json or {},
            model_version=record.model_version,
            confidence_score=record.confidence_score,
            assessment_timestamp=record.assessment_timestamp,
        )

    def get_all_guidelines(self) -> dict:
        return {
            "supported_crops": list(CROP_PROFILES.keys()),
            "profiles": CROP_PROFILES,
        }

