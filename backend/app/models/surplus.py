"""AgriShield AI - Surplus & Aggregation Database Models

Includes SurplusListing, AggregationGroup, and AggregationMember.
Supports optimistic concurrency control with a version column and transaction safety.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class SurplusListing(Base):
    __tablename__ = "surplus_listings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="RESTRICT"), nullable=False, index=True)
    initial_quantity_kg = Column(Float, nullable=False)
    available_quantity_kg = Column(Float, nullable=False)  # Decremented safely on aggregation
    quality_grade = Column(String(30), nullable=False)  # Grade A, Grade B, Grade C, Fair Average Quality
    harvest_timestamp = Column(DateTime(timezone=True), nullable=False)
    expected_price_per_kg = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)

    # Location
    village = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), default="Maharashtra", nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    freshness_assessment_id = Column(String(36), ForeignKey("freshness_assessments.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), default="active", nullable=False, index=True)  # active, partially_allocated, aggregated, sold, cancelled
    version = Column(Integer, default=1, nullable=False)  # Optimistic concurrency lock
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    crop = relationship("Crop")
    farmer = relationship("User")
    freshness_assessment = relationship("FreshnessAssessment")
    aggregation_memberships = relationship("AggregationMember", back_populates="surplus_listing")


class AggregationGroup(Base):
    __tablename__ = "aggregation_groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_code = Column(String(50), unique=True, index=True, nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="RESTRICT"), nullable=False, index=True)
    target_quantity_kg = Column(Float, nullable=False)
    current_quantity_kg = Column(Float, default=0.0, nullable=False)
    target_price_per_kg = Column(Float, nullable=False)

    # Hub Location for collective pickup
    hub_village = Column(String(100), nullable=False)
    hub_district = Column(String(100), nullable=False, index=True)
    hub_latitude = Column(Float, nullable=False)
    hub_longitude = Column(Float, nullable=False)
    max_distance_radius_km = Column(Float, default=25.0, nullable=False)

    expiry_timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="forming", nullable=False, index=True)  # forming, ready_for_offer, offer_matched, in_transit, completed, cancelled
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    crop = relationship("Crop")
    creator = relationship("User")
    members = relationship("AggregationMember", back_populates="group", cascade="all, delete-orphan")


class AggregationMember(Base):
    __tablename__ = "aggregation_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String(36), ForeignKey("aggregation_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    surplus_listing_id = Column(String(36), ForeignKey("surplus_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    committed_quantity_kg = Column(Float, nullable=False)
    joined_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    status = Column(String(30), default="committed", nullable=False)  # committed, released, delivered

    group = relationship("AggregationGroup", back_populates="members")
    farmer = relationship("User")
    surplus_listing = relationship("SurplusListing", back_populates="aggregation_memberships")

