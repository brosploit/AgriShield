"""AgriShield AI - Marketplace & Buyer Offer Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BuyerRequirementCreate(BaseModel):
    crop_id: str
    required_quantity_kg: float = Field(..., gt=0.0)
    quality_grade_requirement: str = Field(..., description="Grade A, Grade B, Grade C, Fair Average Quality")
    target_price_per_kg: float = Field(..., gt=0.0)
    delivery_location: str
    delivery_district: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_deadline: datetime


class BuyerRequirementResponse(BaseModel):
    id: str
    buyer_id: str
    buyer_name: Optional[str] = None
    crop_id: str
    crop_name: Optional[str] = None
    required_quantity_kg: float
    fulfilled_quantity_kg: float
    quality_grade_requirement: str
    target_price_per_kg: float
    delivery_location: str
    delivery_district: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_deadline: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BuyerOfferCreate(BaseModel):
    surplus_listing_id: Optional[str] = None
    aggregation_group_id: Optional[str] = None
    buyer_requirement_id: Optional[str] = None
    offered_price_per_kg: float = Field(..., gt=0.0)
    offered_quantity_kg: float = Field(..., gt=0.0)
    terms: Optional[str] = None
    valid_until: datetime


class BuyerOfferResponse(BaseModel):
    id: str
    buyer_id: str
    buyer_name: Optional[str] = None
    surplus_listing_id: Optional[str] = None
    aggregation_group_id: Optional[str] = None
    buyer_requirement_id: Optional[str] = None
    crop_name: Optional[str] = None
    offered_price_per_kg: float
    offered_quantity_kg: float
    total_amount_inr: float
    terms: Optional[str] = None
    valid_until: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OfferStatusUpdate(BaseModel):
    status: str = Field(..., description="accepted, rejected, counter_offered")
    rejection_reason: Optional[str] = None

