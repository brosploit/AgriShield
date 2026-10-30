"""AgriShield AI - Digital Storage Verification Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StorageFacilityCreate(BaseModel):
    facility_name: str = Field(..., max_length=150)
    facility_type: str = Field(..., description="grain_silo, ventilated_godown, cold_storage, hermetic_warehouse")
    village: str
    district: str
    state: str = "Maharashtra"
    total_capacity_mt: float = Field(..., gt=0.0)
    has_aeration: bool = True
    has_humidity_control: bool = False


class StorageFacilityResponse(StorageFacilityCreate):
    id: str
    cooperative_id: str
    available_capacity_mt: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class StorageBatchCreate(BaseModel):
    farmer_id: Optional[str] = None  # Cooperative admin can register on behalf of farmer, or farmer self-registers
    cooperative_id: str
    facility_id: str
    crop_id: str
    quantity: float = Field(..., gt=0.0)
    unit: str = Field(default="kg", description="kg, quintal, MT")


class StorageInspectionCreate(BaseModel):
    moisture_pct: float = Field(..., ge=0.0, le=100.0)
    temperature_c: float = Field(..., ge=-20.0, le=70.0)
    humidity_pct: float = Field(..., ge=0.0, le=100.0)
    infestation_detected: bool = False
    foreign_matter_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    physical_produce_quality_assessment: str
    inspector_notes: Optional[str] = None


class StorageInspectionResponse(BaseModel):
    id: str
    batch_id: str
    inspector_id: str
    inspector_name: Optional[str] = None
    inspection_timestamp: datetime
    moisture_pct: float
    temperature_c: float
    humidity_pct: float
    infestation_detected: bool
    foreign_matter_pct: float
    physical_quality_score: float
    physical_produce_quality_assessment: str
    inspector_notes: Optional[str] = None
    inspection_hash: str

    model_config = ConfigDict(from_attributes=True)


class VerificationRecordResponse(BaseModel):
    id: str
    batch_id: str
    previous_hash: str
    record_hash: str
    record_authenticity_verified: bool
    inspection_completed: bool
    physical_quality_status: str
    verified_by_id: str
    timestamp: datetime
    payload_snapshot: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class StorageBatchResponse(BaseModel):
    id: str
    batch_identifier: str
    farmer_id: str
    farmer_name: Optional[str] = None
    cooperative_id: str
    cooperative_name: Optional[str] = None
    facility_id: str
    facility_name: Optional[str] = None
    crop_id: str
    crop_name: Optional[str] = None
    quantity: float
    unit: str
    registration_timestamp: datetime
    current_hash: str
    verification_status: str
    created_at: datetime
    inspections: List[StorageInspectionResponse] = []
    verification_records: List[VerificationRecordResponse] = []

    model_config = ConfigDict(from_attributes=True)


class BatchVerificationSummary(BaseModel):
    batch_identifier: str
    record_authenticity: bool
    cryptographic_seal_valid: bool
    current_hash: str
    inspection_completed: bool
    total_inspections: int
    latest_inspection_date: Optional[datetime] = None
    physical_quality_status: str
    moisture_pct: Optional[float] = None
    infestation_detected: Optional[bool] = None
    disclaimer: str = (
        "Cryptographic proof guarantees digital record immutability and authenticity. "
        "Physical grain quality metrics are determined exclusively by physical inspection readings."
    )

