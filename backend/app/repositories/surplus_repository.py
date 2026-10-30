"""AgriShield AI - Surplus & Aggregation Repository

Includes transaction-safe quantity allocation to eliminate race conditions and double allocation.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import DoubleAllocationException, EntityNotFoundException
from app.models.surplus import SurplusListing, AggregationGroup, AggregationMember
from app.utils.geo import haversine_distance_km


class SurplusRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_surplus_listing(self, listing: SurplusListing) -> SurplusListing:
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def get_listing_by_id(self, listing_id: str) -> Optional[SurplusListing]:
        return self.db.query(SurplusListing).filter(SurplusListing.id == listing_id).first()

    def get_listings(
        self,
        crop_id: Optional[str] = None,
        district: Optional[str] = None,
        status: str = "active",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[SurplusListing], int]:
        query = self.db.query(SurplusListing)
        if crop_id:
            query = query.filter(SurplusListing.crop_id == crop_id)
        if district:
            query = query.filter(SurplusListing.district.ilike(district.strip()))
        if status:
            query = query.filter(SurplusListing.status == status)

        total = query.count()
        items = query.order_by(SurplusListing.created_at.desc()).offset(offset).limit(limit).all()
        return items, total

    def find_nearby_listings(
        self,
        latitude: float,
        longitude: float,
        max_radius_km: float = 50.0,
        crop_id: Optional[str] = None,
        quality_grade: Optional[str] = None,
    ) -> List[Tuple[SurplusListing, float]]:
        """Find active surplus listings within geographic radius using Haversine calculation."""
        query = self.db.query(SurplusListing).filter(
            SurplusListing.status.in_(["active", "partially_allocated"]),
            SurplusListing.available_quantity_kg > 0,
        )
        if crop_id:
            query = query.filter(SurplusListing.crop_id == crop_id)
        if quality_grade:
            query = query.filter(SurplusListing.quality_grade == quality_grade)

        candidates = query.all()
        results = []
        for item in candidates:
            dist = haversine_distance_km(latitude, longitude, item.latitude, item.longitude)
            if dist <= max_radius_km:
                results.append((item, dist))

        # Sort by closest first
        results.sort(key=lambda x: x[1])
        return results

    def allocate_quantity_safe(self, listing_id: str, requested_qty_kg: float) -> SurplusListing:
        """Atomically allocate quantity from surplus listing using row-level locking.

        Prevents double allocation under concurrent requests.
        """
        # Execute row lock using SELECT FOR UPDATE
        listing = (
            self.db.query(SurplusListing)
            .filter(SurplusListing.id == listing_id)
            .with_for_update()
            .first()
        )
        if not listing:
            raise EntityNotFoundException("SurplusListing", listing_id)

        if listing.available_quantity_kg < requested_qty_kg:
            raise DoubleAllocationException(
                listing_id=listing_id,
                requested_qty=requested_qty_kg,
                available_qty=listing.available_quantity_kg,
            )

        listing.available_quantity_kg -= requested_qty_kg
        listing.version += 1
        if listing.available_quantity_kg <= 0:
            listing.status = "aggregated"
        else:
            listing.status = "partially_allocated"

        self.db.commit()
        self.db.refresh(listing)
        return listing

    def release_quantity_safe(self, listing_id: str, released_qty_kg: float) -> SurplusListing:
        """Atomically release committed quantity back to surplus pool upon group cancellation or member exit."""
        listing = (
            self.db.query(SurplusListing)
            .filter(SurplusListing.id == listing_id)
            .with_for_update()
            .first()
        )
        if listing:
            listing.available_quantity_kg = min(
                listing.initial_quantity_kg,
                listing.available_quantity_kg + released_qty_kg,
            )
            listing.version += 1
            if listing.available_quantity_kg >= listing.initial_quantity_kg:
                listing.status = "active"
            else:
                listing.status = "partially_allocated"
            self.db.commit()
            self.db.refresh(listing)
        return listing

    # Aggregation Groups
    def create_aggregation_group(self, group: AggregationGroup) -> AggregationGroup:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def get_aggregation_group_by_id(self, group_id: str) -> Optional[AggregationGroup]:
        return self.db.query(AggregationGroup).filter(AggregationGroup.id == group_id).first()

    def get_aggregation_groups(
        self, crop_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50
    ) -> List[AggregationGroup]:
        query = self.db.query(AggregationGroup)
        if crop_id:
            query = query.filter(AggregationGroup.crop_id == crop_id)
        if status:
            query = query.filter(AggregationGroup.status == status)
        return query.order_by(AggregationGroup.created_at.desc()).limit(limit).all()

    def add_group_member(self, member: AggregationMember) -> AggregationMember:
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_group_member(self, group_id: str, farmer_id: str) -> Optional[AggregationMember]:
        member = (
            self.db.query(AggregationMember)
            .filter(
                AggregationMember.group_id == group_id,
                AggregationMember.farmer_id == farmer_id,
                AggregationMember.status == "committed",
            )
            .first()
        )
        if member:
            member.status = "released"
            self.db.commit()
        return member

