"""AgriShield AI - Cooperative Administration API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.exceptions import EntityNotFoundException
from app.core.permissions import UserRole
from app.models.user import CooperativeProfile, User
from app.repositories.user_repository import UserRepository
from app.schemas.storage import StorageFacilityCreate, StorageFacilityResponse
from app.schemas.user import CooperativeProfileCreate, CooperativeProfileResponse
from app.services.storage_verification.storage_service import StorageService

router = APIRouter(prefix="/cooperatives", tags=["Cooperatives"])


@router.post(
    "/profile",
    response_model=CooperativeProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.COOPERATIVE_ADMIN]))],
)
def create_or_update_profile(
    profile_data: CooperativeProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    profile = CooperativeProfile(
        user_id=current_user.id,
        cooperative_name=profile_data.cooperative_name,
        registration_number=profile_data.registration_number,
        district=profile_data.district,
        state=profile_data.state,
        total_member_farmers=profile_data.total_member_farmers,
        contact_email=profile_data.contact_email,
    )
    saved = user_repo.create_or_update_cooperative_profile(profile)
    return saved


@router.get(
    "/profile",
    response_model=CooperativeProfileResponse,
    dependencies=[Depends(require_roles([UserRole.COOPERATIVE_ADMIN]))],
)
def get_my_cooperative_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    profile = user_repo.get_cooperative_profile(current_user.id)
    if not profile:
        raise EntityNotFoundException("CooperativeProfile", current_user.id)
    return profile


@router.post(
    "/facilities",
    response_model=StorageFacilityResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.COOPERATIVE_ADMIN]))],
)
def create_facility(
    request: StorageFacilityCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = StorageService(db)
    return service.create_facility(current_user.id, request)


@router.get(
    "/facilities",
    response_model=List[StorageFacilityResponse],
    dependencies=[Depends(require_roles([UserRole.COOPERATIVE_ADMIN]))],
)
def get_my_facilities(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = StorageService(db)
    return service.get_facilities(cooperative_id=current_user.id)

