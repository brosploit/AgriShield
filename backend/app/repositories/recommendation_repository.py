"""AgriShield AI - Recommendation & Audit Repositories
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation
from app.models.audit import AuditLog, Notification


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, rec: Recommendation) -> Recommendation:
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_by_id(self, rec_id: str) -> Optional[Recommendation]:
        return self.db.query(Recommendation).filter(Recommendation.id == rec_id).first()

    def get_farmer_recommendations(
        self, farmer_id: str, include_dismissed: bool = False, limit: int = 50
    ) -> List[Recommendation]:
        query = self.db.query(Recommendation).filter(Recommendation.farmer_id == farmer_id)
        if not include_dismissed:
            query = query.filter(Recommendation.is_dismissed.is_(False))
        return query.order_by(Recommendation.creation_timestamp.desc()).limit(limit).all()

    def dismiss(self, rec_id: str, farmer_id: str) -> Optional[Recommendation]:
        rec = (
            self.db.query(Recommendation)
            .filter(Recommendation.id == rec_id, Recommendation.farmer_id == farmer_id)
            .first()
        )
        if rec:
            rec.is_dismissed = True
            self.db.commit()
            self.db.refresh(rec)
        return rec


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        details: dict,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(log)
        self.db.commit()
        return log

    def create_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        category: str = "general",
        data: Optional[dict] = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            body=body,
            category=category,
            data=data,
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def get_user_notifications(self, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read.is_(False))
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_notification_read(self, notif_id: str, user_id: str) -> Optional[Notification]:
        notif = self.db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user_id).first()
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif

