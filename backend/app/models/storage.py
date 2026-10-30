"""AgriShield AI - Digital Storage Verification Database Models

Includes StorageFacility, StorageBatch, StorageInspection, and VerificationRecord.
Implements tamper-evident cryptographic hash chaining while explicitly separating
record authenticity, inspection completion, and physical grain quality.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
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


class StorageFacility(Base):
    __tablename__ = "storage_facilities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cooperative_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_name = Column(String(150), nullable=False)
    facility_type = Column(String(50), nullable=False)  # grain_silo, ventilated_godown, cold_storage, hermetic_warehouse
    village = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), default="Maharashtra", nullable=False)
    total_capacity_mt = Column(Float, nullable=False)
    available_capacity_mt = Column(Float, nullable=False)
    has_aeration = Column(Boolean, default=True, nullable=False)
    has_humidity_control = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    cooperative = relationship("User")
    batches = relationship("StorageBatch", back_populates="facility")


class StorageBatch(Base):
    __tablename__ = "storage_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_identifier = Column(String(50), unique=True, index=True, nullable=False)  # e.g. BATCH-202610-GRAIN-0012
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    cooperative_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    facility_id = Column(String(36), ForeignKey("storage_facilities.id", ondelete="RESTRICT"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(10), default="kg", nullable=False)  # kg, quintal, MT
    registration_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Cryptographic integrity seal
    current_hash = Column(String(64), nullable=False)
    verification_status = Column(String(30), default="UNVERIFIED", nullable=False, index=True)  # UNVERIFIED, PENDING_INSPECTION, VERIFIED, REJECTED, DISCHARGED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    farmer = relationship("User", foreign_keys=[farmer_id])
    cooperative = relationship("User", foreign_keys=[cooperative_id])
    facility = relationship("StorageFacility", back_populates="batches")
    crop = relationship("Crop")
    inspections = relationship("StorageInspection", back_populates="batch", cascade="all, delete-orphan", order_by="StorageInspection.inspection_timestamp.desc()")
    verification_records = relationship("VerificationRecord", back_populates="batch", cascade="all, delete-orphan", order_by="VerificationRecord.timestamp.desc()")


class StorageInspection(Base):
    __tablename__ = "storage_inspections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("storage_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    inspector_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    inspection_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Measured Physical Produce Parameters (distinct from cryptographic proof)
    moisture_pct = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    infestation_detected = Column(Boolean, default=False, nullable=False)
    foreign_matter_pct = Column(Float, default=0.0, nullable=False)
    physical_quality_score = Column(Float, nullable=False)  # 0 to 100
    physical_produce_quality_assessment = Column(Text, nullable=False)  # e.g. "Safe moisture level (11.8%), no insect pests detected"
    inspector_notes = Column(Text, nullable=True)

    # Inspection log hash
    inspection_hash = Column(String(64), nullable=False)

    batch = relationship("StorageBatch", back_populates="inspections")
    inspector = relationship("User")


class VerificationRecord(Base):
    """Tamper-evident verification audit trail.

    Maintains append-only cryptographic hashes chaining all batch events and inspections.
    """
    __tablename__ = "verification_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("storage_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_hash = Column(String(64), nullable=False)
    record_hash = Column(String(64), nullable=False)  # SHA-256(previous_hash + payload_snapshot)

    # Tri-part status flags
    record_authenticity_verified = Column(Boolean, default=True, nullable=False)
    inspection_completed = Column(Boolean, default=False, nullable=False)
    physical_quality_status = Column(String(30), nullable=False)  # EXCELLENT, GOOD, MARGINAL, COMPROMISED

    verified_by_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    payload_snapshot = Column(JSON, nullable=False)

    batch = relationship("StorageBatch", back_populates="verification_records")
    verified_by = relationship("User")

