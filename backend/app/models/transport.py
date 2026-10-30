"""AgriShield AI - Transportation & Shipment Database Models

Includes TransportRequest, TransportOffer, and Shipment.
Supports route estimation, vehicle pairing, and delivery verification.
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
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class TransportRequest(Base):
    __tablename__ = "transport_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    aggregation_group_id = Column(String(36), ForeignKey("aggregation_groups.id", ondelete="SET NULL"), nullable=True, index=True)
    surplus_listing_id = Column(String(36), ForeignKey("surplus_listings.id", ondelete="SET NULL"), nullable=True, index=True)
    crop_id = Column(String(36), ForeignKey("crops.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_weight_kg = Column(Float, nullable=False)

    pickup_location = Column(Text, nullable=False)
    pickup_latitude = Column(Float, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    delivery_location = Column(Text, nullable=False)
    delivery_latitude = Column(Float, nullable=False)
    delivery_longitude = Column(Float, nullable=False)

    pickup_window_start = Column(DateTime(timezone=True), nullable=False)
    pickup_window_end = Column(DateTime(timezone=True), nullable=False)
    estimated_distance_km = Column(Float, nullable=False)
    estimated_cost_inr = Column(Float, nullable=False)
    requires_cold_chain = Column(Boolean, default=False, nullable=False)

    status = Column(String(30), default="open", nullable=False, index=True)  # open, assigned, in_transit, delivered, cancelled
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    requester = relationship("User")
    crop = relationship("Crop")
    aggregation_group = relationship("AggregationGroup")
    surplus_listing = relationship("SurplusListing")
    offers = relationship("TransportOffer", back_populates="transport_request", cascade="all, delete-orphan")
    shipment = relationship("Shipment", back_populates="transport_request", uselist=False)


class TransportOffer(Base):
    __tablename__ = "transport_offers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transport_request_id = Column(String(36), ForeignKey("transport_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    transporter_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(String(36), ForeignKey("transporter_profiles.id", ondelete="SET NULL"), nullable=True)
    offered_rate_total_inr = Column(Float, nullable=False)
    pickup_datetime_proposed = Column(DateTime(timezone=True), nullable=False)
    estimated_delivery_datetime = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="submitted", nullable=False, index=True)  # submitted, accepted, rejected, expired
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    transport_request = relationship("TransportRequest", back_populates="offers")
    transporter = relationship("User")
    vehicle = relationship("TransporterProfile")


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transport_request_id = Column(String(36), ForeignKey("transport_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    transport_offer_id = Column(String(36), ForeignKey("transport_offers.id", ondelete="CASCADE"), nullable=False)
    transporter_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    actual_pickup_timestamp = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_timestamp = Column(DateTime(timezone=True), nullable=True)
    current_status = Column(String(30), default="ASSIGNED", nullable=False, index=True)  # ASSIGNED, DISPATCHED, PICKED_UP, IN_TRANSIT, DELIVERED, CONFIRMED
    delivery_confirmation_otp = Column(String(10), nullable=True)
    delivery_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    transport_request = relationship("TransportRequest", back_populates="shipment")
    transport_offer = relationship("TransportOffer")
    transporter = relationship("User")

