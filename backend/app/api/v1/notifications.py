"""AgriShield AI - Rural In-App Notifications API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.exceptions import EntityNotFoundException
from app.models.user import User
from app.repositories.recommendation_repository import AuditRepository
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_my_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    audit_repo = AuditRepository(db)
    return audit_repo.get_user_notifications(current_user.id, unread_only=unread_only, limit=limit)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    audit_repo = AuditRepository(db)
    notif = audit_repo.mark_notification_read(notification_id, current_user.id)
    if not notif:
        raise EntityNotFoundException("Notification", notification_id)
    return notif

