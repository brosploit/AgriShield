"""AgriShield AI - Unified Recommendation Database Model

Connects Freshness, Surplus Aggregation, Buyer Market, Transportation,
and Storage Verification into actionable, explainable farmer guidance.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    related_crop_id = Column(String(36), ForeignKey("crops.id", ondelete="SET NULL"), nullable=True, index=True)
    related_batch_id = Column(String(36), ForeignKey("storage_batches.id", ondelete="SET NULL"), nullable=True, index=True)

    category = Column(String(50), nullable=False, index=True)
    # Categories:
    # 1. URGENT_SALE
    # 2. SURPLUS_AGGREGATION
    # 3. OFFER_COMPARISON
    # 4. COLLECTIVE_TRANSPORT
    # 5. COOPERATIVE_STORAGE
    # 6. STORAGE_INSPECTION
    # 7. COST_OPTIMIZATION

    priority = Column(String(20), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    explanation = Column(Text, nullable=False)
    supporting_information = Column(JSON, nullable=False)
    suggested_action = Column(Text, nullable=False)
    is_dismissed = Column(Boolean, default=False, nullable=False)
    creation_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    farmer = relationship("User")
    crop = relationship("Crop")
    batch = relationship("StorageBatch")

