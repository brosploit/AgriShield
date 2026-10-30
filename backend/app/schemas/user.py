"""AgriShield AI - User Profile Schemas

Schemas for Farmer, Buyer, Transporter, and Cooperative profiles.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Farmer Profile
class FarmerProfileCreate(BaseModel):
    village: str = Field(..., max_length=100)
    taluka_or_tehsil: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    state: str = Field(default="Maharashtra", max_length=100)
    pincode: str = Field(..., pattern=r"^[1-9][0-9]{5}$")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    total_land_acres: Optional[float] = Field(None, ge=0.0)
    primary_crops: Optional[List[str]] = Field(default_factory=list)
    preferred_language: str = Field(default="mr", max_length=10)


class FarmerProfileResponse(FarmerProfileCreate):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)


# Buyer Profile
class BuyerProfileCreate(BaseModel):
    business_name: str = Field(..., max_length=150)
    business_type: str = Field(..., max_length=50)  # wholesaler, retailer, food_processor, exporter
    gst_number: Optional[str] = Field(None, max_length=20)
    city: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    pincode: str = Field(..., pattern=r"^[1-9][0-9]{5}$")
    delivery_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BuyerProfileResponse(BuyerProfileCreate):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)


# Transporter Profile
class TransporterProfileCreate(BaseModel):
    vehicle_type: str = Field(..., max_length=50)
    vehicle_registration_number: str = Field(..., max_length=30)
    capacity_tonnes: float = Field(..., gt=0.0)
    has_refrigeration: bool = False
    operating_radius_km: float = Field(default=100.0, gt=0.0)
    base_city: str = Field(..., max_length=100)
    base_latitude: Optional[float] = None
    base_longitude: Optional[float] = None
    rate_per_km_inr: float = Field(default=25.0, gt=0.0)
    is_available: bool = True


class TransporterProfileResponse(TransporterProfileCreate):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)


# Cooperative Profile
class CooperativeProfileCreate(BaseModel):
    cooperative_name: str = Field(..., max_length=150)
    registration_number: str = Field(..., max_length=50)
    district: str = Field(..., max_length=100)
    state: str = Field(default="Maharashtra", max_length=100)
    total_member_farmers: int = Field(default=0, ge=0)
    contact_email: Optional[EmailStr] = None


class CooperativeProfileResponse(CooperativeProfileCreate):
    id: str
    user_id: str

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

