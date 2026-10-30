"""AgriShield AI - Platform Administration & System Audit API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.exceptions import EntityNotFoundException
from app.core.permissions import UserRole
from app.models.audit import AuditLog
from app.models.crop import Crop, FreshnessAssessment
from app.models.marketplace import BuyerOffer
from app.models.storage import StorageBatch
from app.models.surplus import AggregationGroup, SurplusListing
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/admin", tags=["Platform Administration"])


@router.get(
    "/stats",
    dependencies=[Depends(require_roles([UserRole.PLATFORM_ADMIN]))],
)
def get_system_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    total_users = db.query(User).count()
    total_farmers = db.query(User).filter(User.role == UserRole.FARMER.value).count()
    total_buyers = db.query(User).filter(User.role == UserRole.BUYER.value).count()
    total_transporters = db.query(User).filter(User.role == UserRole.TRANSPORTER.value).count()
    total_cooperatives = db.query(User).filter(User.role == UserRole.COOPERATIVE_ADMIN.value).count()

    total_surplus_active = db.query(SurplusListing).filter(SurplusListing.status == "active").count()
    total_aggregation_groups = db.query(AggregationGroup).count()
    total_storage_batches = db.query(StorageBatch).count()
    total_assessments = db.query(FreshnessAssessment).count()
    total_offers = db.query(BuyerOffer).count()

    return {
        "users": {
            "total": total_users,
            "farmers": total_farmers,
            "buyers": total_buyers,
            "transporters": total_transporters,
            "cooperatives": total_cooperatives,
        },
        "operations": {
            "active_surplus_listings": total_surplus_active,
            "aggregation_groups": total_aggregation_groups,
            "storage_batches": total_storage_batches,
            "freshness_assessments": total_assessments,
            "marketplace_offers": total_offers,
        },
    }


@router.get(
    "/audit-logs",
    dependencies=[Depends(require_roles([UserRole.PLATFORM_ADMIN]))],
)
def get_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    action: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    dependencies=[Depends(require_roles([UserRole.PLATFORM_ADMIN]))],
)
def update_user_status(
    user_id: str,
    is_active: bool,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise EntityNotFoundException("User", user_id)

    user.is_active = is_active
    saved = user_repo.update_user(user)
    return saved

