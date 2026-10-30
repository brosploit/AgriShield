"""AgriShield AI - Marketplace & Negotiation Service

Manages Buyer Requirements, Offers, Offer Comparison, and Acceptance Workflows.
Ensures only authorized asset owners (farmer or group admin) can accept/reject offers.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import (
    AgriShieldException,
    EntityNotFoundException,
    PermissionDeniedException,
)
from app.models.marketplace import BuyerOffer, BuyerRequirement
from app.models.surplus import AggregationGroup, SurplusListing
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.surplus_repository import SurplusRepository
from app.repositories.recommendation_repository import AuditRepository
from app.schemas.marketplace import (
    BuyerOfferCreate,
    BuyerOfferResponse,
    BuyerRequirementCreate,
    BuyerRequirementResponse,
    OfferStatusUpdate,
)


class MarketplaceService:
    def __init__(self, db: Session):
        self.db = db
        self.market_repo = MarketplaceRepository(db)
        self.surplus_repo = SurplusRepository(db)
        self.audit_repo = AuditRepository(db)

    def create_requirement(self, buyer_id: str, request: BuyerRequirementCreate) -> BuyerRequirementResponse:
        req = BuyerRequirement(
            buyer_id=buyer_id,
            crop_id=request.crop_id,
            required_quantity_kg=request.required_quantity_kg,
            fulfilled_quantity_kg=0.0,
            quality_grade_requirement=request.quality_grade_requirement,
            target_price_per_kg=request.target_price_per_kg,
            delivery_location=request.delivery_location,
            delivery_district=request.delivery_district,
            delivery_latitude=request.delivery_latitude,
            delivery_longitude=request.delivery_longitude,
            delivery_deadline=request.delivery_deadline,
            status="open",
        )
        saved = self.market_repo.create_requirement(req)
        return self._build_requirement_response(saved)

    def get_requirements(
        self, crop_id: Optional[str] = None, district: Optional[str] = None, status: str = "open"
    ) -> List[BuyerRequirementResponse]:
        reqs = self.market_repo.get_requirements(crop_id=crop_id, district=district, status=status)
        return [self._build_requirement_response(r) for r in reqs]

    def get_requirement(self, req_id: str) -> BuyerRequirementResponse:
        req = self.market_repo.get_requirement_by_id(req_id)
        if not req:
            raise EntityNotFoundException("BuyerRequirement", req_id)
        return self._build_requirement_response(req)

    def create_offer(self, buyer_id: str, request: BuyerOfferCreate) -> BuyerOfferResponse:
        if not request.surplus_listing_id and not request.aggregation_group_id:
            raise AgriShieldException("An offer must target either a surplus listing or an aggregation group.", status_code=400)

        total_amount = round(request.offered_price_per_kg * request.offered_quantity_kg, 2)

        offer = BuyerOffer(
            buyer_id=buyer_id,
            surplus_listing_id=request.surplus_listing_id,
            aggregation_group_id=request.aggregation_group_id,
            buyer_requirement_id=request.buyer_requirement_id,
            offered_price_per_kg=request.offered_price_per_kg,
            offered_quantity_kg=request.offered_quantity_kg,
            total_amount_inr=total_amount,
            terms=request.terms,
            valid_until=request.valid_until,
            status="pending",
        )
        saved = self.market_repo.create_offer(offer)

        # Notify recipient
        if request.surplus_listing_id:
            listing = self.surplus_repo.get_listing_by_id(request.surplus_listing_id)
            if listing:
                self.audit_repo.create_notification(
                    user_id=listing.farmer_id,
                    title="New Buyer Offer Received",
                    body=f"Buyer offered ₹{offer.offered_price_per_kg}/kg for {offer.offered_quantity_kg} kg.",
                    category="offer",
                    data={"offer_id": saved.id, "listing_id": listing.id},
                )

        return self._build_offer_response(saved)

    def get_offers(
        self, surplus_listing_id: Optional[str] = None, aggregation_group_id: Optional[str] = None
    ) -> List[BuyerOfferResponse]:
        if surplus_listing_id:
            offers = self.market_repo.get_offers_for_surplus(surplus_listing_id)
        elif aggregation_group_id:
            offers = self.market_repo.get_offers_for_aggregation_group(aggregation_group_id)
        else:
            offers = self.db.query(BuyerOffer).order_by(BuyerOffer.created_at.desc()).limit(50).all()

        return [self._build_offer_response(o) for o in offers]

    def get_offer(self, offer_id: str) -> BuyerOfferResponse:
        offer = self.market_repo.get_offer_by_id(offer_id)
        if not offer:
            raise EntityNotFoundException("BuyerOffer", offer_id)
        return self._build_offer_response(offer)

    def update_offer_status(self, user_id: str, offer_id: str, update: OfferStatusUpdate) -> BuyerOfferResponse:
        offer = self.market_repo.get_offer_by_id(offer_id)
        if not offer:
            raise EntityNotFoundException("BuyerOffer", offer_id)

        # Authorization Check: verify user is the farmer who owns the surplus OR creator of the group
        is_authorized = False
        if offer.surplus_listing_id:
            listing = self.surplus_repo.get_listing_by_id(offer.surplus_listing_id)
            if listing and listing.farmer_id == user_id:
                is_authorized = True
        elif offer.aggregation_group_id:
            group = self.surplus_repo.get_aggregation_group_by_id(offer.aggregation_group_id)
            if group and group.created_by_id == user_id:
                is_authorized = True

        if not is_authorized:
            raise PermissionDeniedException("Only the produce owner or group creator can accept/reject this offer.")

        offer = self.market_repo.update_offer_status(offer, update.status)

        # If offer accepted, update asset status
        if update.status == "accepted":
            if offer.surplus_listing_id:
                listing = self.surplus_repo.get_listing_by_id(offer.surplus_listing_id)
                if listing:
                    listing.status = "sold"
                    self.db.commit()
            elif offer.aggregation_group_id:
                group = self.surplus_repo.get_aggregation_group_by_id(offer.aggregation_group_id)
                if group:
                    group.status = "offer_matched"
                    self.db.commit()

            # Notify buyer
            self.audit_repo.create_notification(
                user_id=offer.buyer_id,
                title="Offer Accepted!",
                body=f"Your offer of ₹{offer.offered_price_per_kg}/kg was accepted.",
                category="offer",
                data={"offer_id": offer.id},
            )

        return self._build_offer_response(offer)

    def _build_requirement_response(self, req: BuyerRequirement) -> BuyerRequirementResponse:
        return BuyerRequirementResponse(
            id=req.id,
            buyer_id=req.buyer_id,
            buyer_name=req.buyer.full_name if req.buyer else None,
            crop_id=req.crop_id,
            crop_name=req.crop.name if req.crop else None,
            required_quantity_kg=req.required_quantity_kg,
            fulfilled_quantity_kg=req.fulfilled_quantity_kg,
            quality_grade_requirement=req.quality_grade_requirement,
            target_price_per_kg=req.target_price_per_kg,
            delivery_location=req.delivery_location,
            delivery_district=req.delivery_district,
            delivery_latitude=req.delivery_latitude,
            delivery_longitude=req.delivery_longitude,
            delivery_deadline=req.delivery_deadline,
            status=req.status,
            created_at=req.created_at,
        )

    def _build_offer_response(self, offer: BuyerOffer) -> BuyerOfferResponse:
        crop_name = None
        if offer.surplus_listing and offer.surplus_listing.crop:
            crop_name = offer.surplus_listing.crop.name
        elif offer.aggregation_group and offer.aggregation_group.crop:
            crop_name = offer.aggregation_group.crop.name

        return BuyerOfferResponse(
            id=offer.id,
            buyer_id=offer.buyer_id,
            buyer_name=offer.buyer.full_name if offer.buyer else None,
            surplus_listing_id=offer.surplus_listing_id,
            aggregation_group_id=offer.aggregation_group_id,
            buyer_requirement_id=offer.buyer_requirement_id,
            crop_name=crop_name,
            offered_price_per_kg=offer.offered_price_per_kg,
            offered_quantity_kg=offer.offered_quantity_kg,
            total_amount_inr=offer.total_amount_inr,
            terms=offer.terms,
            valid_until=offer.valid_until,
            status=offer.status,
            created_at=offer.created_at,
            updated_at=offer.updated_at,
        )

