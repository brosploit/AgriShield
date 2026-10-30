"""AgriShield AI - Marketplace & Buyer Offer Database Models

Includes BuyerRequirement and BuyerOffer.
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
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class BuyerRequirement(Base):
    __tablename__ = "buyer_requirements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="RESTRICT"), nullable=False, index=True)
    required_quantity_kg = Column(Float, nullable=False)
    fulfilled_quantity_kg = Column(Float, default=0.0, nullable=False)
    quality_grade_requirement = Column(String(50), nullable=False)
    target_price_per_kg = Column(Float, nullable=False)
    delivery_location = Column(Text, nullable=False)
    delivery_district = Column(String(100), nullable=False, index=True)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    delivery_deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="open", nullable=False, index=True)  # open, partially_fulfilled, fulfilled, expired, cancelled
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    buyer = relationship("User")
    crop = relationship("Crop")
    offers = relationship("BuyerOffer", back_populates="buyer_requirement")


class BuyerOffer(Base):
    __tablename__ = "buyer_offers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    surplus_listing_id = Column(String(36), ForeignKey("surplus_listings.id", ondelete="SET NULL"), nullable=True, index=True)
    aggregation_group_id = Column(String(36), ForeignKey("aggregation_groups.id", ondelete="SET NULL"), nullable=True, index=True)
    buyer_requirement_id = Column(String(36), ForeignKey("buyer_requirements.id", ondelete="SET NULL"), nullable=True, index=True)
    offered_price_per_kg = Column(Float, nullable=False)
    offered_quantity_kg = Column(Float, nullable=False)
    total_amount_inr = Column(Float, nullable=False)
    terms = Column(Text, nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="pending", nullable=False, index=True)  # pending, accepted, rejected, expired, counter_offered
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    buyer = relationship("User")
    surplus_listing = relationship("SurplusListing")
    aggregation_group = relationship("AggregationGroup")
    buyer_requirement = relationship("BuyerRequirement", back_populates="offers")

