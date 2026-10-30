"""AgriShield AI - Digital Storage Verification API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import User
from app.schemas.storage import (
    BatchVerificationSummary,
    StorageBatchCreate,
    StorageBatchResponse,
    StorageFacilityCreate,
    StorageFacilityResponse,
    StorageInspectionCreate,
    StorageInspectionResponse,
)
from app.services.storage_verification.storage_service import StorageService

router = APIRouter(prefix="/storage", tags=["Digital Storage Verification"])


@router.post(
    "/batches",
    response_model=StorageBatchResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.FARMER, UserRole.COOPERATIVE_ADMIN]))],
)
def register_grain_batch(
    request: StorageBatchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = StorageService(db)
    return service.register_batch(current_user.id, request)


@router.get("/batches", response_model=List[StorageBatchResponse])
def get_batches(
    farmer_id: Optional[str] = None,
    cooperative_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = StorageService(db)
    return service.get_batches(farmer_id=farmer_id, cooperative_id=cooperative_id)


@router.get("/batches/{batch_id}", response_model=StorageBatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    service = StorageService(db)
    return service.get_batch(batch_id)


@router.post(
    "/batches/{batch_id}/inspect",
    response_model=StorageInspectionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.COOPERATIVE_ADMIN]))],
)
def record_batch_inspection(
    batch_id: str,
    request: StorageInspectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = StorageService(db)
    return service.record_inspection(current_user.id, batch_id, request)


@router.get("/batches/{batch_id}/verification", response_model=BatchVerificationSummary)
def verify_batch_cryptographic_record(batch_id: str, db: Session = Depends(get_db)):
    service = StorageService(db)
    return service.verify_batch_integrity(batch_id)


@router.get("/cooperatives", response_model=List[StorageFacilityResponse])
def get_cooperative_facilities(
    cooperative_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = StorageService(db)
    return service.get_facilities(cooperative_id=cooperative_id)

