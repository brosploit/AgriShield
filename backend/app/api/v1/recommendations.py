"""AgriShield AI - Unified AI Recommendations API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import User
from app.schemas.recommendation import (
    GenerateRecommendationsRequest,
    RecommendationResponse,
)
from app.services.recommendation_engine.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Unified AI Recommendations"])


@router.get(
    "",
    response_model=List[RecommendationResponse],
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def get_farmer_recommendations(
    include_dismissed: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    return service.get_farmer_recommendations(current_user.id, include_dismissed=include_dismissed)


@router.post(
    "/generate",
    response_model=List[RecommendationResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def trigger_recommendation_generation(
    request: GenerateRecommendationsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    farmer_id = request.farmer_id if request.farmer_id and current_user.role == UserRole.PLATFORM_ADMIN.value else current_user.id
    return service.generate_recommendations_for_farmer(farmer_id)


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    return service.get_recommendation(recommendation_id)

