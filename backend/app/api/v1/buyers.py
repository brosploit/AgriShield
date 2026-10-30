"""AgriShield AI - Buyer Requirements & Offers API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import BuyerProfile, User
from app.repositories.user_repository import UserRepository
from app.schemas.marketplace import (
    BuyerOfferCreate,
    BuyerOfferResponse,
    BuyerRequirementCreate,
    BuyerRequirementResponse,
    OfferStatusUpdate,
)
from app.schemas.user import BuyerProfileCreate, BuyerProfileResponse
from app.services.marketplace_service import MarketplaceService

router = APIRouter(tags=["Buyers & Marketplace"])


@router.post(
    "/buyers/profile",
    response_model=BuyerProfileResponse,
    dependencies=[Depends(require_roles([UserRole.BUYER]))],
)
def create_buyer_profile(
    data: BuyerProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    profile = BuyerProfile(
        user_id=current_user.id,
        business_name=data.business_name,
        business_type=data.business_type,
        gst_number=data.gst_number,
        city=data.city,
        district=data.district,
        state=data.state,
        pincode=data.pincode,
        delivery_address=data.delivery_address,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    saved = user_repo.create_or_update_buyer_profile(profile)
    return saved


@router.post(
    "/buyers/requirements",
    response_model=BuyerRequirementResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.BUYER]))],
)
def create_requirement(
    req_data: BuyerRequirementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.create_requirement(current_user.id, req_data)


@router.get("/buyers/requirements", response_model=List[BuyerRequirementResponse])
def get_requirements(
    crop_id: Optional[str] = None,
    district: Optional[str] = None,
    status: str = "open",
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.get_requirements(crop_id=crop_id, district=district, status=status)


@router.get("/buyers/requirements/{requirement_id}", response_model=BuyerRequirementResponse)
def get_requirement(requirement_id: str, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_requirement(requirement_id)


# Offer endpoints
@router.post(
    "/offers",
    response_model=BuyerOfferResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.BUYER]))],
)
def create_offer(
    offer_data: BuyerOfferCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.create_offer(current_user.id, offer_data)


@router.get("/offers", response_model=List[BuyerOfferResponse])
def list_offers(
    surplus_listing_id: Optional[str] = None,
    aggregation_group_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.get_offers(
        surplus_listing_id=surplus_listing_id,
        aggregation_group_id=aggregation_group_id,
    )


@router.get("/offers/{offer_id}", response_model=BuyerOfferResponse)
def get_offer(offer_id: str, db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_offer(offer_id)


@router.patch("/offers/{offer_id}/status", response_model=BuyerOfferResponse)
def update_offer_status(
    offer_id: str,
    update: OfferStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.update_offer_status(current_user.id, offer_id, update)

