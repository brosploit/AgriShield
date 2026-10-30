"""AgriShield AI - Smart Aggregation API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import User
from app.schemas.surplus import (
    AggregationGroupCreate,
    AggregationGroupResponse,
    JoinAggregationRequest,
)
from app.services.aggregation_engine.aggregation_service import AggregationService

router = APIRouter(prefix="/aggregation", tags=["Smart Surplus Aggregation"])


@router.post(
    "/create",
    response_model=AggregationGroupResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.FARMER, UserRole.COOPERATIVE_ADMIN]))],
)
def create_aggregation_group(
    request: AggregationGroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AggregationService(db)
    return service.create_group(current_user.id, request)


@router.get("/groups", response_model=List[AggregationGroupResponse])
def get_aggregation_groups(
    crop_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = AggregationService(db)
    return service.get_groups(crop_id=crop_id, status=status)


@router.get("/groups/{group_id}", response_model=AggregationGroupResponse)
def get_aggregation_group(group_id: str, db: Session = Depends(get_db)):
    service = AggregationService(db)
    return service.get_group(group_id)


@router.post(
    "/{group_id}/join",
    response_model=AggregationGroupResponse,
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def join_aggregation_group(
    group_id: str,
    request: JoinAggregationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AggregationService(db)
    return service.join_group(current_user.id, group_id, request)


@router.post(
    "/{group_id}/leave",
    response_model=AggregationGroupResponse,
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def leave_aggregation_group(
    group_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AggregationService(db)
    return service.leave_group(current_user.id, group_id)

