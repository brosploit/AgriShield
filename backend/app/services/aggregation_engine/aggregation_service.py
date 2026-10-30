"""AgriShield AI - Smart Surplus Aggregation Engine

Connects nearby farmers with compatible surplus to form collective bulk shipment lots,
calculates pooled transportation savings, and enforces double-allocation safety.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import (
    AgriShieldException,
    EntityNotFoundException,
    PermissionDeniedException,
)
from app.models.crop import Crop
from app.models.surplus import AggregationGroup, AggregationMember, SurplusListing
from app.repositories.crop_repository import CropRepository
from app.repositories.surplus_repository import SurplusRepository
from app.schemas.surplus import (
    AggregationGroupCreate,
    AggregationGroupResponse,
    AggregationMemberResponse,
    JoinAggregationRequest,
)
from app.utils.geo import haversine_distance_km, estimate_transport_cost_inr


class AggregationService:
    def __init__(self, db: Session):
        self.db = db
        self.surplus_repo = SurplusRepository(db)
        self.crop_repo = CropRepository(db)

    def create_group(self, user_id: str, request: AggregationGroupCreate) -> AggregationGroupResponse:
        crop = self.crop_repo.get_crop_by_id(request.crop_id)
        if not crop:
            raise EntityNotFoundException("Crop", request.crop_id)

        # Generate unique readable group code
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:4].upper()
        group_code = f"AGG-{date_str}-{crop.name[:3].upper()}-{rand_suffix}"

        group = AggregationGroup(
            group_code=group_code,
            crop_id=request.crop_id,
            target_quantity_kg=request.target_quantity_kg,
            current_quantity_kg=0.0,
            target_price_per_kg=request.target_price_per_kg,
            hub_village=request.hub_village,
            hub_district=request.hub_district,
            hub_latitude=request.hub_latitude,
            hub_longitude=request.hub_longitude,
            max_distance_radius_km=request.max_distance_radius_km,
            expiry_timestamp=request.expiry_timestamp,
            status="forming",
            created_by_id=user_id,
        )
        saved_group = self.surplus_repo.create_aggregation_group(group)

        # If creator commits an initial surplus batch
        if request.initial_surplus_listing_id and request.initial_committed_qty_kg:
            self.join_group(
                user_id=user_id,
                group_id=saved_group.id,
                request=JoinAggregationRequest(
                    surplus_listing_id=request.initial_surplus_listing_id,
                    committed_quantity_kg=request.initial_committed_qty_kg,
                ),
            )
            # Re-fetch group after initial member addition
            saved_group = self.surplus_repo.get_aggregation_group_by_id(saved_group.id)

        return self._build_response(saved_group)

    def join_group(self, user_id: str, group_id: str, request: JoinAggregationRequest) -> AggregationGroupResponse:
        group = self.surplus_repo.get_aggregation_group_by_id(group_id)
        if not group:
            raise EntityNotFoundException("AggregationGroup", group_id)

        if group.status not in ["forming", "ready_for_offer"]:
            raise AgriShieldException(f"Aggregation group '{group.group_code}' is currently closed ({group.status}).", status_code=400)

        listing = self.surplus_repo.get_listing_by_id(request.surplus_listing_id)
        if not listing:
            raise EntityNotFoundException("SurplusListing", request.surplus_listing_id)

        if listing.farmer_id != user_id:
            raise PermissionDeniedException("You can only commit surplus listings that you own.")

        # 1. Crop Compatibility Check
        if listing.crop_id != group.crop_id:
            raise AgriShieldException("Incompatible crop. Listing crop does not match aggregation group crop.", status_code=400)

        # 2. Geographic Proximity Check
        dist = haversine_distance_km(listing.latitude, listing.longitude, group.hub_latitude, group.hub_longitude)
        if dist > group.max_distance_radius_km:
            raise AgriShieldException(
                f"Surplus location is {dist} km away, exceeding group's maximum pickup radius of {group.max_distance_radius_km} km.",
                status_code=400,
            )

        # 3. Transaction-safe quantity allocation
        self.surplus_repo.allocate_quantity_safe(listing.id, request.committed_quantity_kg)

        # 4. Record membership
        member = AggregationMember(
            group_id=group.id,
            farmer_id=user_id,
            surplus_listing_id=listing.id,
            committed_quantity_kg=request.committed_quantity_kg,
            status="committed",
        )
        self.surplus_repo.add_group_member(member)

        # 5. Update group total
        group.current_quantity_kg += request.committed_quantity_kg
        if group.current_quantity_kg >= group.target_quantity_kg:
            group.status = "ready_for_offer"
        self.db.commit()
        self.db.refresh(group)

        return self._build_response(group)

    def leave_group(self, user_id: str, group_id: str) -> AggregationGroupResponse:
        group = self.surplus_repo.get_aggregation_group_by_id(group_id)
        if not group:
            raise EntityNotFoundException("AggregationGroup", group_id)

        # Find member record
        member = (
            self.db.query(AggregationMember)
            .filter(
                AggregationMember.group_id == group_id,
                AggregationMember.farmer_id == user_id,
                AggregationMember.status == "committed",
            )
            .first()
        )
        if not member:
            raise EntityNotFoundException("AggregationMembership", f"group={group_id}, farmer={user_id}")

        # Safely release quantity back to surplus pool
        qty = member.committed_quantity_kg
        self.surplus_repo.release_quantity_safe(member.surplus_listing_id, qty)

        # Update member status
        member.status = "released"

        # Update group volume
        group.current_quantity_kg = max(0.0, group.current_quantity_kg - qty)
        if group.current_quantity_kg < group.target_quantity_kg and group.status == "ready_for_offer":
            group.status = "forming"

        self.db.commit()
        self.db.refresh(group)

        return self._build_response(group)

    def get_group(self, group_id: str) -> AggregationGroupResponse:
        group = self.surplus_repo.get_aggregation_group_by_id(group_id)
        if not group:
            raise EntityNotFoundException("AggregationGroup", group_id)
        return self._build_response(group)

    def get_groups(self, crop_id: Optional[str] = None, status: Optional[str] = None) -> List[AggregationGroupResponse]:
        groups = self.surplus_repo.get_aggregation_groups(crop_id=crop_id, status=status)
        return [self._build_response(g) for g in groups]

    def _build_response(self, group: AggregationGroup) -> AggregationGroupResponse:
        members_response = []
        for m in group.members:
            if m.status == "committed":
                farmer_name = m.farmer.full_name if m.farmer else None
                members_response.append(
                    AggregationMemberResponse(
                        id=m.id,
                        group_id=m.group_id,
                        farmer_id=m.farmer_id,
                        farmer_name=farmer_name,
                        surplus_listing_id=m.surplus_listing_id,
                        committed_quantity_kg=m.committed_quantity_kg,
                        joined_at=m.joined_at,
                        status=m.status,
                    )
                )

        return AggregationGroupResponse(
            id=group.id,
            group_code=group.group_code,
            crop_id=group.crop_id,
            crop_name=group.crop.name if group.crop else None,
            target_quantity_kg=group.target_quantity_kg,
            current_quantity_kg=group.current_quantity_kg,
            target_price_per_kg=group.target_price_per_kg,
            hub_village=group.hub_village,
            hub_district=group.hub_district,
            hub_latitude=group.hub_latitude,
            hub_longitude=group.hub_longitude,
            max_distance_radius_km=group.max_distance_radius_km,
            expiry_timestamp=group.expiry_timestamp,
            status=group.status,
            created_by_id=group.created_by_id,
            created_at=group.created_at,
            members=members_response,
        )

