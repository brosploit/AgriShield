"""AgriShield AI - Unified AI Recommendation Engine

The central multi-criteria intelligence component of AgriShield AI.
Connects Freshness, Surplus Aggregation, Buyer Market, Transportation,
and Storage Verification to generate explainable, high-impact farmer guidance.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.models.crop import Crop, FreshnessAssessment
from app.models.marketplace import BuyerOffer, BuyerRequirement
from app.models.recommendation import Recommendation
from app.models.storage import StorageBatch, StorageFacility
from app.models.surplus import AggregationGroup, SurplusListing
from app.repositories.crop_repository import CropRepository
from app.repositories.marketplace_repository import MarketplaceRepository
from app.repositories.recommendation_repository import AuditRepository, RecommendationRepository
from app.repositories.storage_repository import StorageRepository
from app.repositories.surplus_repository import SurplusRepository
from app.repositories.transport_repository import TransportRepository
from app.schemas.recommendation import RecommendationResponse


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.rec_repo = RecommendationRepository(db)
        self.crop_repo = CropRepository(db)
        self.surplus_repo = SurplusRepository(db)
        self.market_repo = MarketplaceRepository(db)
        self.storage_repo = StorageRepository(db)
        self.transport_repo = TransportRepository(db)
        self.audit_repo = AuditRepository(db)

    def generate_recommendations_for_farmer(self, farmer_id: str) -> List[RecommendationResponse]:
        """Synthesize multi-modal agricultural signals across all modules to generate

        explainable recommendations for the specified farmer.
        """
        generated: List[Recommendation] = []

        # Fetch farmer context
        farmer_listings = (
            self.db.query(SurplusListing)
            .filter(SurplusListing.farmer_id == farmer_id, SurplusListing.status.in_(["active", "partially_allocated"]))
            .all()
        )
        recent_assessments = self.crop_repo.get_farmer_assessments(farmer_id, limit=10)
        farmer_batches = self.storage_repo.get_batches(farmer_id=farmer_id)

        # -------------------------------------------------------------
        # Rule 1: High Deterioration Risk -> URGENT SALE RECOMMENDATION
        # -------------------------------------------------------------
        for assessment in recent_assessments:
            if assessment.risk_score >= 50.0:
                priority = "CRITICAL" if assessment.risk_score >= 75.0 else "HIGH"
                crop_name = assessment.crop.name if assessment.crop else "Produce"

                # Check if matching buyer requirements exist in the district
                matching_buyers = (
                    self.db.query(BuyerRequirement)
                    .filter(
                        BuyerRequirement.crop_id == assessment.crop_id,
                        BuyerRequirement.status == "open",
                    )
                    .all()
                )

                buyer_info = (
                    f"{len(matching_buyers)} active buyer requirement(s) found in the region."
                    if matching_buyers
                    else "No immediate direct buyer found; consider local mandi dispatch or instant aggregation."
                )

                rec = Recommendation(
                    farmer_id=farmer_id,
                    related_crop_id=assessment.crop_id,
                    category="URGENT_SALE",
                    priority=priority,
                    explanation=(
                        f"Post-harvest deterioration risk for your {crop_name} is at {assessment.risk_score}% ({assessment.risk_category}). "
                        f"Adverse storage conditions ({assessment.current_temperature_c}°C, {assessment.current_humidity_pct}% RH) threaten produce loss within {assessment.estimated_urgency}."
                    ),
                    supporting_information={
                        "risk_score": assessment.risk_score,
                        "risk_category": assessment.risk_category,
                        "temperature_c": assessment.current_temperature_c,
                        "humidity_pct": assessment.current_humidity_pct,
                        "crop_quantity_kg": assessment.crop_quantity_kg,
                        "matching_buyers_count": len(matching_buyers),
                        "model_version": assessment.model_version,
                    },
                    suggested_action=(
                        f"Prioritize immediate sale or processing of your {assessment.crop_quantity_kg} kg of {crop_name}. "
                        f"{buyer_info}"
                    ),
                )
                generated.append(self.rec_repo.create(rec))

        # -----------------------------------------------------------------
        # Rule 2: Small Surplus Volume -> COMBINE WITH NEARBY FARMERS
        # -----------------------------------------------------------------
        for listing in farmer_listings:
            if listing.available_quantity_kg < 2000.0:  # Under 2 tonnes (sub-truckload)
                # Find nearby compatible surplus
                nearby = self.surplus_repo.find_nearby_listings(
                    latitude=listing.latitude,
                    longitude=listing.longitude,
                    max_radius_km=30.0,
                    crop_id=listing.crop_id,
                )
                # Exclude self
                other_nearby = [item for item, dist in nearby if item.farmer_id != farmer_id]

                if other_nearby:
                    total_nearby_volume = sum(item.available_quantity_kg for item in other_nearby)
                    rec = Recommendation(
                        farmer_id=farmer_id,
                        related_crop_id=listing.crop_id,
                        category="SURPLUS_AGGREGATION",
                        priority="HIGH",
                        explanation=(
                            f"Your surplus of {listing.available_quantity_kg} kg {listing.crop.name if listing.crop else 'crop'} is below standard truckload capacity. "
                            f"Found {len(other_nearby)} nearby farmers within 30 km holding an additional {round(total_nearby_volume, 1)} kg."
                        ),
                        supporting_information={
                            "listing_id": listing.id,
                            "your_quantity_kg": listing.available_quantity_kg,
                            "nearby_farmers_count": len(other_nearby),
                            "total_combined_volume_kg": listing.available_quantity_kg + total_nearby_volume,
                            "radius_km": 30.0,
                        },
                        suggested_action=(
                            f"Create or join a Smart Aggregation Group for {listing.crop.name if listing.crop else 'produce'} "
                            f"to achieve bulk bargaining power and attract institutional wholesale buyers."
                        ),
                    )
                    generated.append(self.rec_repo.create(rec))

        # -------------------------------------------------------------
        # Rule 3: Offers Received -> COMPARE AND EVALUATE BUYER OFFERS
        # -------------------------------------------------------------
        for listing in farmer_listings:
            offers = self.market_repo.get_offers_for_surplus(listing.id)
            pending_offers = [o for o in offers if o.status == "pending"]
            if pending_offers:
                best_offer = max(pending_offers, key=lambda x: x.offered_price_per_kg)
                rec = Recommendation(
                    farmer_id=farmer_id,
                    related_crop_id=listing.crop_id,
                    category="OFFER_COMPARISON",
                    priority="HIGH",
                    explanation=(
                        f"You have {len(pending_offers)} pending buyer offer(s) for listing '{listing.id[:8]}'. "
                        f"Top offer is ₹{best_offer.offered_price_per_kg}/kg from buyer {best_offer.buyer.full_name if best_offer.buyer else 'Anonymous'} "
                        f"(your expected price: ₹{listing.expected_price_per_kg}/kg)."
                    ),
                    supporting_information={
                        "total_offers": len(pending_offers),
                        "highest_offer_price": best_offer.offered_price_per_kg,
                        "expected_price": listing.expected_price_per_kg,
                        "offered_quantity_kg": best_offer.offered_quantity_kg,
                        "total_payout_inr": best_offer.total_amount_inr,
                    },
                    suggested_action="Review and accept the highest verified buyer offer before the offer expires.",
                )
                generated.append(self.rec_repo.create(rec))

        # -----------------------------------------------------------------
        # Rule 4: Durable Grain with Low Moisture -> STORE IN COOPERATIVE
        # -----------------------------------------------------------------
        for listing in farmer_listings:
            crop = listing.crop
            if crop and crop.category in ["durable_grain", "pulse", "oilseed"]:
                # Check available cooperative storage facilities in the district
                facilities = self.storage_repo.get_all_facilities()
                district_facs = [f for f in facilities if f.district.lower() == listing.district.lower() and f.available_capacity_mt > 5.0]

                if district_facs:
                    rec = Recommendation(
                        farmer_id=farmer_id,
                        related_crop_id=listing.crop_id,
                        category="COOPERATIVE_STORAGE",
                        priority="MEDIUM",
                        explanation=(
                            f"Your {crop.name} is a durable crop suitable for scientific long-term storage. "
                            f"{len(district_facs)} verified cooperative warehouse(s) with available capacity exist in {listing.district}."
                        ),
                        supporting_information={
                            "crop": crop.name,
                            "category": crop.category,
                            "district_facilities_count": len(district_facs),
                            "recommended_storage": district_facs[0].facility_name,
                        },
                        suggested_action=(
                            f"Deposit your grain into '{district_facs[0].facility_name}' to obtain a digitally verified warehouse receipt "
                            f"and avoid distress-selling during peak post-harvest arrival price slumps."
                        ),
                    )
                    generated.append(self.rec_repo.create(rec))

        # -------------------------------------------------------------
        # Rule 5: Storage Batches -> SCHEDULE STORAGE INSPECTION
        # -------------------------------------------------------------
        for batch in farmer_batches:
            if batch.verification_status in ["PENDING_INSPECTION", "UNVERIFIED"]:
                rec = Recommendation(
                    farmer_id=farmer_id,
                    related_batch_id=batch.id,
                    related_crop_id=batch.crop_id,
                    category="STORAGE_INSPECTION",
                    priority="HIGH",
                    explanation=(
                        f"Stored grain batch '{batch.batch_identifier}' currently has verification status '{batch.verification_status}'. "
                        f"Moisture and infestation levels must be officially recorded to generate a tamper-evident quality certificate."
                    ),
                    supporting_information={
                        "batch_identifier": batch.batch_identifier,
                        "quantity": batch.quantity,
                        "unit": batch.unit,
                        "facility": batch.facility.facility_name if batch.facility else "Unknown",
                    },
                    suggested_action="Request a cooperative inspection to verify moisture content and secure certified grade status.",
                )
                generated.append(self.rec_repo.create(rec))

        return [self._build_response(r) for r in generated]

    def get_farmer_recommendations(
        self, farmer_id: str, include_dismissed: bool = False
    ) -> List[RecommendationResponse]:
        recs = self.rec_repo.get_farmer_recommendations(farmer_id, include_dismissed=include_dismissed)
        # If no active recommendations exist, trigger dynamic generation
        if not recs:
            return self.generate_recommendations_for_farmer(farmer_id)
        return [self._build_response(r) for r in recs]

    def get_recommendation(self, rec_id: str) -> RecommendationResponse:
        rec = self.rec_repo.get_by_id(rec_id)
        if not rec:
            raise EntityNotFoundException("Recommendation", rec_id)
        return self._build_response(rec)

    def _build_response(self, r: Recommendation) -> RecommendationResponse:
        return RecommendationResponse(
            id=r.id,
            farmer_id=r.farmer_id,
            related_crop_id=r.related_crop_id,
            crop_name=r.crop.name if r.crop else None,
            related_batch_id=r.related_batch_id,
            batch_identifier=r.batch.batch_identifier if r.batch else None,
            category=r.category,
            priority=r.priority,
            explanation=r.explanation,
            supporting_information=r.supporting_information or {},
            suggested_action=r.suggested_action,
            is_dismissed=r.is_dismissed,
            creation_timestamp=r.creation_timestamp,
        )

