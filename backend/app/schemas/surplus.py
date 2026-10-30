"""AgriShield AI - Surplus & Aggregation Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SurplusListingCreate(BaseModel):
    crop_id: str
    quantity_kg: float = Field(..., gt=0.0)
    quality_grade: str = Field(..., description="Grade A, Grade B, Grade C, Fair Average Quality")
    harvest_timestamp: datetime
    expected_price_per_kg: float = Field(..., gt=0.0)
    currency: str = "INR"
    village: str
    district: str
    state: str = "Maharashtra"
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    freshness_assessment_id: Optional[str] = None


class SurplusListingResponse(BaseModel):
    id: str
    farmer_id: str
    crop_id: str
    crop_name: Optional[str] = None
    initial_quantity_kg: float
    available_quantity_kg: float
    quality_grade: str
    harvest_timestamp: datetime
    expected_price_per_kg: float
    currency: str
    village: str
    district: str
    state: str
    latitude: float
    longitude: float
    freshness_assessment_id: Optional[str] = None
    status: str
    created_at: datetime
    distance_km: Optional[float] = None  # Included in nearby search responses

    model_config = ConfigDict(from_attributes=True)


class NearbySurplusQuery(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    max_radius_km: float = Field(default=50.0, gt=0.0, le=500.0)
    crop_id: Optional[str] = None
    quality_grade: Optional[str] = None


class AggregationGroupCreate(BaseModel):
    crop_id: str
    target_quantity_kg: float = Field(..., gt=0.0)
    target_price_per_kg: float = Field(..., gt=0.0)
    hub_village: str
    hub_district: str
    hub_latitude: float = Field(..., ge=-90.0, le=90.0)
    hub_longitude: float = Field(..., ge=-180.0, le=180.0)
    max_distance_radius_km: float = Field(default=25.0, gt=0.0)
    expiry_timestamp: datetime
    initial_surplus_listing_id: Optional[str] = None
    initial_committed_qty_kg: Optional[float] = None


class AggregationMemberResponse(BaseModel):
    id: str
    group_id: str
    farmer_id: str
    farmer_name: Optional[str] = None
    surplus_listing_id: str
    committed_quantity_kg: float
    joined_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class AggregationGroupResponse(BaseModel):
    id: str
    group_code: str
    crop_id: str
    crop_name: Optional[str] = None
    target_quantity_kg: float
    current_quantity_kg: float
    target_price_per_kg: float
    hub_village: str
    hub_district: str
    hub_latitude: float
    hub_longitude: float
    max_distance_radius_km: float
    expiry_timestamp: datetime
    status: str
    created_by_id: str
    created_at: datetime
    members: List[AggregationMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)


class JoinAggregationRequest(BaseModel):
    surplus_listing_id: str
    committed_quantity_kg: float = Field(..., gt=0.0)

