"""AgriShield AI - Crop & Freshness Assessment Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CropBase(BaseModel):
    name: str = Field(..., max_length=100)
    hindi_name: Optional[str] = None
    marathi_name: Optional[str] = None
    category: str = Field(..., description="perishable_vegetable, perishable_fruit, durable_grain, pulse, oilseed")
    standard_shelf_life_days: float = Field(..., gt=0)
    optimal_temp_min_c: float
    optimal_temp_max_c: float
    optimal_humidity_min_pct: float = Field(..., ge=0, le=100)
    optimal_humidity_max_pct: float = Field(..., ge=0, le=100)
    respiration_rate: str = "medium"
    ethylene_sensitivity: str = "medium"


class CropCreate(CropBase):
    pass


class CropResponse(CropBase):
    id: str

    model_config = ConfigDict(from_attributes=True)


class CropGuidelineCreate(BaseModel):
    crop_id: str
    storage_type: str = Field(..., description="open_air, traditional_shed, ventilated_godown, cold_storage, hermetic_silo")
    critical_temp_threshold_c: float
    critical_humidity_threshold_pct: float
    max_safe_storage_days: float
    recommended_handling: str
    post_harvest_care_tips: str


class CropGuidelineResponse(CropGuidelineCreate):
    id: str

    model_config = ConfigDict(from_attributes=True)


class FreshnessAssessmentRequest(BaseModel):
    crop_id: Optional[str] = None
    crop_name: Optional[str] = Field(None, description="Crop name (e.g., Tomato, Onion, Wheat) if crop_id is not known")
    harvest_datetime: datetime
    current_temperature_c: float = Field(..., ge=-10.0, le=60.0)
    current_humidity_pct: float = Field(..., ge=0.0, le=100.0)
    storage_type: str = Field(..., description="open_air, traditional_shed, ventilated_godown, cold_storage, hermetic_silo")
    storage_duration_hours: float = Field(..., ge=0.0)
    transportation_conditions: str = Field(default="ambient_open", description="ambient_open, covered, ventilated, refrigerated")
    crop_quantity_kg: float = Field(..., gt=0.0)
    sensor_readings: Optional[Dict[str, Any]] = None


class FreshnessAssessmentResponse(BaseModel):
    id: str
    farmer_id: str
    crop_id: str
    crop_name: str
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Deterioration risk score from 0 to 100")
    risk_category: str = Field(..., description="Low, Moderate, High, Critical")
    estimated_urgency: str
    recommended_action: str
    influencing_factors: Dict[str, Any]
    model_version: str
    confidence_score: Optional[float] = None
    assessment_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

