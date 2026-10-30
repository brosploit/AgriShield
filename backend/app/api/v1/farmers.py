"""AgriShield AI - Farmer Profile & Data Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.exceptions import EntityNotFoundException
from app.core.permissions import UserRole
from app.models.surplus import SurplusListing
from app.models.user import FarmerProfile, User
from app.repositories.user_repository import UserRepository
from app.schemas.surplus import SurplusListingResponse
from app.schemas.user import FarmerProfileCreate, FarmerProfileResponse

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.post(
    "/profile",
    response_model=FarmerProfileResponse,
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def create_or_update_profile(
    profile_data: FarmerProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    profile = FarmerProfile(
        user_id=current_user.id,
        village=profile_data.village,
        taluka_or_tehsil=profile_data.taluka_or_tehsil,
        district=profile_data.district,
        state=profile_data.state,
        pincode=profile_data.pincode,
        latitude=profile_data.latitude,
        longitude=profile_data.longitude,
        total_land_acres=profile_data.total_land_acres,
        primary_crops=profile_data.primary_crops,
        preferred_language=profile_data.preferred_language,
    )
    saved = user_repo.create_or_update_farmer_profile(profile)
    return saved


@router.get(
    "/profile",
    response_model=FarmerProfileResponse,
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def get_farmer_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    profile = user_repo.get_farmer_profile(current_user.id)
    if not profile:
        raise EntityNotFoundException("FarmerProfile", current_user.id)
    return profile


@router.get(
    "/listings",
    response_model=List[SurplusListingResponse],
    dependencies=[Depends(require_roles([UserRole.FARMER]))],
)
def get_my_surplus_listings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    listings = (
        db.query(SurplusListing)
        .filter(SurplusListing.farmer_id == current_user.id)
        .order_by(SurplusListing.created_at.desc())
        .all()
    )
    return [
        SurplusListingResponse(
            id=item.id,
            farmer_id=item.farmer_id,
            crop_id=item.crop_id,
            crop_name=item.crop.name if item.crop else None,
            initial_quantity_kg=item.initial_quantity_kg,
            available_quantity_kg=item.available_quantity_kg,
            quality_grade=item.quality_grade,
            harvest_timestamp=item.harvest_timestamp,
            expected_price_per_kg=item.expected_price_per_kg,
            currency=item.currency,
            village=item.village,
            district=item.district,
            state=item.state,
            latitude=item.latitude,
            longitude=item.longitude,
            freshness_assessment_id=item.freshness_assessment_id,
            status=item.status,
            created_at=item.created_at,
        )
        for item in listings
    ]

