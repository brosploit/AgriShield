"""AgriShield AI - Smart Surplus Management Service

Handles surplus registration, spatial discovery, and transaction-safe availability.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import EntityNotFoundException
from app.models.crop import Crop
from app.models.surplus import SurplusListing
from app.repositories.crop_repository import CropRepository
from app.repositories.surplus_repository import SurplusRepository
from app.schemas.surplus import SurplusListingCreate, SurplusListingResponse


class SurplusService:
    def __init__(self, db: Session):
        self.db = db
        self.surplus_repo = SurplusRepository(db)
        self.crop_repo = CropRepository(db)

    def register_surplus(self, farmer_id: str, request: SurplusListingCreate) -> SurplusListingResponse:
        crop = self.crop_repo.get_crop_by_id(request.crop_id)
        if not crop:
            raise EntityNotFoundException("Crop", request.crop_id)

        listing = SurplusListing(
            farmer_id=farmer_id,
            crop_id=request.crop_id,
            initial_quantity_kg=request.quantity_kg,
            available_quantity_kg=request.quantity_kg,
            quality_grade=request.quality_grade,
            harvest_timestamp=request.harvest_timestamp,
            expected_price_per_kg=request.expected_price_per_kg,
            currency=request.currency,
            village=request.village,
            district=request.district,
            state=request.state,
            latitude=request.latitude,
            longitude=request.longitude,
            freshness_assessment_id=request.freshness_assessment_id,
            status="active",
        )
        saved = self.surplus_repo.create_surplus_listing(listing)

        return SurplusListingResponse(
            id=saved.id,
            farmer_id=saved.farmer_id,
            crop_id=saved.crop_id,
            crop_name=crop.name,
            initial_quantity_kg=saved.initial_quantity_kg,
            available_quantity_kg=saved.available_quantity_kg,
            quality_grade=saved.quality_grade,
            harvest_timestamp=saved.harvest_timestamp,
            expected_price_per_kg=saved.expected_price_per_kg,
            currency=saved.currency,
            village=saved.village,
            district=saved.district,
            state=saved.state,
            latitude=saved.latitude,
            longitude=saved.longitude,
            freshness_assessment_id=saved.freshness_assessment_id,
            status=saved.status,
            created_at=saved.created_at,
        )

    def get_listing(self, listing_id: str) -> SurplusListingResponse:
        listing = self.surplus_repo.get_listing_by_id(listing_id)
        if not listing:
            raise EntityNotFoundException("SurplusListing", listing_id)

        return SurplusListingResponse(
            id=listing.id,
            farmer_id=listing.farmer_id,
            crop_id=listing.crop_id,
            crop_name=listing.crop.name if listing.crop else None,
            initial_quantity_kg=listing.initial_quantity_kg,
            available_quantity_kg=listing.available_quantity_kg,
            quality_grade=listing.quality_grade,
            harvest_timestamp=listing.harvest_timestamp,
            expected_price_per_kg=listing.expected_price_per_kg,
            currency=listing.currency,
            village=listing.village,
            district=listing.district,
            state=listing.state,
            latitude=listing.latitude,
            longitude=listing.longitude,
            freshness_assessment_id=listing.freshness_assessment_id,
            status=listing.status,
            created_at=listing.created_at,
        )

    def get_listings(
        self,
        crop_id: Optional[str] = None,
        district: Optional[str] = None,
        status: str = "active",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[SurplusListingResponse], int]:
        items, total = self.surplus_repo.get_listings(
            crop_id=crop_id, district=district, status=status, limit=limit, offset=offset
        )
        responses = [
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
            for item in items
        ]
        return responses, total

    def find_nearby(
        self,
        latitude: float,
        longitude: float,
        max_radius_km: float = 50.0,
        crop_id: Optional[str] = None,
        quality_grade: Optional[str] = None,
    ) -> List[SurplusListingResponse]:
        results = self.surplus_repo.find_nearby_listings(
            latitude=latitude,
            longitude=longitude,
            max_radius_km=max_radius_km,
            crop_id=crop_id,
            quality_grade=quality_grade,
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
                distance_km=dist,
            )
            for item, dist in results
        ]

