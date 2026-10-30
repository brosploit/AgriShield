"""AgriShield AI - User & Profile Database Models

Includes User, FarmerProfile, BuyerProfile, TransporterProfile,
CooperativeProfile, and RefreshToken.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships to profiles
    farmer_profile = relationship("FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    buyer_profile = relationship("BuyerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transporter_profile = relationship("TransporterProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    cooperative_profile = relationship("CooperativeProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Tokens & notifications
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    village = Column(String(100), nullable=False, index=True)
    taluka_or_tehsil = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), default="Maharashtra", nullable=False)
    pincode = Column(String(10), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    total_land_acres = Column(Float, nullable=True)
    primary_crops = Column(JSON, default=list)
    preferred_language = Column(String(10), default="mr")

    user = relationship("User", back_populates="farmer_profile")


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    business_name = Column(String(150), nullable=False)
    business_type = Column(String(50), nullable=False)  # wholesaler, retailer, food_processor, exporter
    gst_number = Column(String(20), nullable=True)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    delivery_address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    user = relationship("User", back_populates="buyer_profile")


class TransporterProfile(Base):
    __tablename__ = "transporter_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    vehicle_registration_number = Column(String(30), unique=True, nullable=False, index=True)
    capacity_tonnes = Column(Float, nullable=False)
    has_refrigeration = Column(Boolean, default=False, nullable=False)
    operating_radius_km = Column(Float, default=100.0, nullable=False)
    base_city = Column(String(100), nullable=False)
    base_latitude = Column(Float, nullable=True)
    base_longitude = Column(Float, nullable=True)
    rate_per_km_inr = Column(Float, default=25.0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="transporter_profile")


class CooperativeProfile(Base):
    __tablename__ = "cooperative_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    cooperative_name = Column(String(150), nullable=False)
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    total_member_farmers = Column(Integer, default=0, nullable=False)
    contact_email = Column(String(100), nullable=True)

    user = relationship("User", back_populates="cooperative_profile")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    jti = Column(String(64), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")

