"""AgriShield AI - Surplus Listing API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.surplus import SurplusListingCreate, SurplusListingResponse
from app.services.surplus_engine.surplus_service import SurplusService

router = APIRouter(prefix="/surplus", tags=["Smart Surplus"])


@router.post(
    "/register",
    response_model=SurplusListingResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def register_surplus(
    request: SurplusListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = SurplusService(db)
    return service.register_surplus(current_user.id, request)


@router.get("/listings", response_model=PaginatedResponse[SurplusListingResponse])
def get_listings(
    crop_id: Optional[str] = None,
    district: Optional[str] = None,
    status: str = "active",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = SurplusService(db)
    offset = (page - 1) * page_size
    items, total = service.get_listings(
        crop_id=crop_id, district=district, status=status, limit=page_size, offset=offset
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/nearby", response_model=List[SurplusListingResponse])
def get_nearby_surplus(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    max_radius_km: float = Query(default=50.0, gt=0.0, le=500.0),
    crop_id: Optional[str] = None,
    quality_grade: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = SurplusService(db)
    return service.find_nearby(
        latitude=latitude,
        longitude=longitude,
        max_radius_km=max_radius_km,
        crop_id=crop_id,
        quality_grade=quality_grade,
    )


@router.get("/{listing_id}", response_model=SurplusListingResponse)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    service = SurplusService(db)
    return service.get_listing(listing_id)

