"""AgriShield AI - Freshness Intelligence API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import User
from app.schemas.crop import FreshnessAssessmentRequest, FreshnessAssessmentResponse
from app.services.freshness_engine.freshness_service import FreshnessService

router = APIRouter(prefix="/freshness", tags=["AI Freshness Intelligence"])


@router.post(
    "/assess",
    response_model=FreshnessAssessmentResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles([UserRole.FARMER, UserRole.COOPERATIVE_ADMIN]))],
)
def assess_crop_freshness(
    request: FreshnessAssessmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = FreshnessService(db)
    return service.assess_freshness(request, farmer_id=current_user.id)


@router.get(
    "/history",
    response_model=List[FreshnessAssessmentResponse],
    dependencies=[Depends(require_roles([UserRole.FARMER, UserRole.COOPERATIVE_ADMIN]))],
)
def get_assessment_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = FreshnessService(db)
    return service.get_history(farmer_id=current_user.id)


@router.get("/crop-guidelines")
def get_crop_guidelines(db: Session = Depends(get_db)):
    service = FreshnessService(db)
    return service.get_all_guidelines()


@router.get("/{assessment_id}", response_model=FreshnessAssessmentResponse)
def get_assessment_by_id(assessment_id: str, db: Session = Depends(get_db)):
    service = FreshnessService(db)
    return service.get_assessment(assessment_id)

