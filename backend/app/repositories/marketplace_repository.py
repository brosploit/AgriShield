"""AgriShield AI - Marketplace & Offer Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.marketplace import BuyerRequirement, BuyerOffer


class MarketplaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_requirement(self, requirement: BuyerRequirement) -> BuyerRequirement:
        self.db.add(requirement)
        self.db.commit()
        self.db.refresh(requirement)
        return requirement

    def get_requirement_by_id(self, req_id: str) -> Optional[BuyerRequirement]:
        return self.db.query(BuyerRequirement).filter(BuyerRequirement.id == req_id).first()

    def get_requirements(
        self, crop_id: Optional[str] = None, district: Optional[str] = None, status: str = "open", limit: int = 50
    ) -> List[BuyerRequirement]:
        query = self.db.query(BuyerRequirement)
        if crop_id:
            query = query.filter(BuyerRequirement.crop_id == crop_id)
        if district:
            query = query.filter(BuyerRequirement.delivery_district.ilike(district.strip()))
        if status:
            query = query.filter(BuyerRequirement.status == status)
        return query.order_by(BuyerRequirement.created_at.desc()).limit(limit).all()

    def create_offer(self, offer: BuyerOffer) -> BuyerOffer:
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_offer_by_id(self, offer_id: str) -> Optional[BuyerOffer]:
        return self.db.query(BuyerOffer).filter(BuyerOffer.id == offer_id).first()

    def get_offers_for_surplus(self, listing_id: str) -> List[BuyerOffer]:
        return (
            self.db.query(BuyerOffer)
            .filter(BuyerOffer.surplus_listing_id == listing_id)
            .order_by(BuyerOffer.offered_price_per_kg.desc())
            .all()
        )

    def get_offers_for_aggregation_group(self, group_id: str) -> List[BuyerOffer]:
        return (
            self.db.query(BuyerOffer)
            .filter(BuyerOffer.aggregation_group_id == group_id)
            .order_by(BuyerOffer.offered_price_per_kg.desc())
            .all()
        )

    def update_offer_status(self, offer: BuyerOffer, new_status: str) -> BuyerOffer:
        offer.status = new_status
        self.db.commit()
        self.db.refresh(offer)
        return offer

