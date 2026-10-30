"""AgriShield AI - Transportation & Shipment Schemas
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TransportRequestCreate(BaseModel):
    aggregation_group_id: Optional[str] = None
    surplus_listing_id: Optional[str] = None
    crop_id: str
    total_weight_kg: float = Field(..., gt=0.0)
    pickup_location: str
    pickup_latitude: float = Field(..., ge=-90.0, le=90.0)
    pickup_longitude: float = Field(..., ge=-180.0, le=180.0)
    delivery_location: str
    delivery_latitude: float = Field(..., ge=-90.0, le=90.0)
    delivery_longitude: float = Field(..., ge=-180.0, le=180.0)
    pickup_window_start: datetime
    pickup_window_end: datetime
    requires_cold_chain: bool = False


class TransportOfferCreate(BaseModel):
    transport_request_id: str
    vehicle_id: Optional[str] = None
    offered_rate_total_inr: float = Field(..., gt=0.0)
    pickup_datetime_proposed: datetime
    estimated_delivery_datetime: datetime


class TransportOfferResponse(BaseModel):
    id: str
    transport_request_id: str
    transporter_id: str
    transporter_name: Optional[str] = None
    vehicle_id: Optional[str] = None
    vehicle_type: Optional[str] = None
    offered_rate_total_inr: float
    pickup_datetime_proposed: datetime
    estimated_delivery_datetime: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransportRequestResponse(BaseModel):
    id: str
    requester_id: str
    aggregation_group_id: Optional[str] = None
    surplus_listing_id: Optional[str] = None
    crop_id: str
    crop_name: Optional[str] = None
    total_weight_kg: float
    pickup_location: str
    pickup_latitude: float
    pickup_longitude: float
    delivery_location: str
    delivery_latitude: float
    delivery_longitude: float
    pickup_window_start: datetime
    pickup_window_end: datetime
    estimated_distance_km: float
    estimated_cost_inr: float
    requires_cold_chain: bool
    status: str
    created_at: datetime
    offers: List[TransportOfferResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ShipmentStatusUpdate(BaseModel):
    status: str = Field(..., description="ASSIGNED, DISPATCHED, PICKED_UP, IN_TRANSIT, DELIVERED, CONFIRMED")
    delivery_confirmation_otp: Optional[str] = None
    delivery_notes: Optional[str] = None


class ShipmentResponse(BaseModel):
    id: str
    transport_request_id: str
    transport_offer_id: str
    transporter_id: str
    transporter_name: Optional[str] = None
    actual_pickup_timestamp: Optional[datetime] = None
    actual_delivery_timestamp: Optional[datetime] = None
    current_status: str
    delivery_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

