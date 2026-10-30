"""AgriShield AI - Crop & Freshness Assessment Database Models

Includes Crop, CropGuideline, and FreshnessAssessment.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Crop(Base):
    __tablename__ = "crops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    hindi_name = Column(String(100), nullable=True)
    marathi_name = Column(String(100), nullable=True)
    category = Column(String(50), nullable=False)  # perishable_vegetable, perishable_fruit, durable_grain, pulse, oilseed
    standard_shelf_life_days = Column(Float, nullable=False)
    optimal_temp_min_c = Column(Float, nullable=False)
    optimal_temp_max_c = Column(Float, nullable=False)
    optimal_humidity_min_pct = Column(Float, nullable=False)
    optimal_humidity_max_pct = Column(Float, nullable=False)
    respiration_rate = Column(String(20), default="medium", nullable=False)
    ethylene_sensitivity = Column(String(20), default="medium", nullable=False)

    guidelines = relationship("CropGuideline", back_populates="crop", cascade="all, delete-orphan")
    freshness_assessments = relationship("FreshnessAssessment", back_populates="crop")


class CropGuideline(Base):
    __tablename__ = "crop_guidelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True)
    storage_type = Column(String(50), nullable=False)  # open_air, traditional_shed, ventilated_godown, cold_storage, hermetic_silo
    critical_temp_threshold_c = Column(Float, nullable=False)
    critical_humidity_threshold_pct = Column(Float, nullable=False)
    max_safe_storage_days = Column(Float, nullable=False)
    recommended_handling = Column(Text, nullable=False)
    post_harvest_care_tips = Column(Text, nullable=False)

    crop = relationship("Crop", back_populates="guidelines")


class FreshnessAssessment(Base):
    __tablename__ = "freshness_assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False, index=True)
    harvest_datetime = Column(DateTime(timezone=True), nullable=False)
    current_temperature_c = Column(Float, nullable=False)
    current_humidity_pct = Column(Float, nullable=False)
    storage_type = Column(String(50), nullable=False)
    storage_duration_hours = Column(Float, nullable=False)
    transportation_conditions = Column(String(50), default="ambient_open", nullable=False)
    crop_quantity_kg = Column(Float, nullable=False)
    sensor_readings_json = Column(JSON, nullable=True)

    # Assessment outputs
    risk_score = Column(Float, nullable=False)  # 0 to 100
    risk_category = Column(String(20), nullable=False, index=True)  # Low, Moderate, High, Critical
    estimated_urgency = Column(String(50), nullable=False)
    recommended_action = Column(Text, nullable=False)
    influencing_factors_json = Column(JSON, nullable=False)
    model_version = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=True)
    assessment_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    crop = relationship("Crop", back_populates="freshness_assessments")
    farmer = relationship("User")

