"""AgriShield AI - Transportation Coordination Service

Manages transporter profiles, route queries, shipment requests, transporter bidding,
and delivery lifecycle confirmations.
"""

from datetime import datetime, timezone
import random
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import (
    AgriShieldException,
    EntityNotFoundException,
    PermissionDeniedException,
)
from app.models.transport import Shipment, TransportOffer, TransportRequest
from app.models.user import TransporterProfile, User
from app.repositories.transport_repository import TransportRepository
from app.repositories.recommendation_repository import AuditRepository
from app.schemas.transport import (
    ShipmentResponse,
    ShipmentStatusUpdate,
    TransportOfferCreate,
    TransportOfferResponse,
    TransportRequestCreate,
    TransportRequestResponse,
)
from app.schemas.user import TransporterProfileCreate, TransporterProfileResponse
from app.utils.geo import estimate_transport_cost_inr, haversine_distance_km


class TransportService:
    def __init__(self, db: Session):
        self.db = db
        self.transport_repo = TransportRepository(db)
        self.audit_repo = AuditRepository(db)

    def register_transporter(self, user_id: str, request: TransporterProfileCreate) -> TransporterProfileResponse:
        profile = TransporterProfile(
            user_id=user_id,
            vehicle_type=request.vehicle_type,
            vehicle_registration_number=request.vehicle_registration_number,
            capacity_tonnes=request.capacity_tonnes,
            has_refrigeration=request.has_refrigeration,
            operating_radius_km=request.operating_radius_km,
            base_city=request.base_city,
            base_latitude=request.base_latitude,
            base_longitude=request.base_longitude,
            rate_per_km_inr=request.rate_per_km_inr,
            is_available=request.is_available,
        )
        saved = self.db.merge(profile)
        self.db.commit()
        self.db.refresh(saved)

        return TransporterProfileResponse(
            id=saved.id,
            user_id=saved.user_id,
            vehicle_type=saved.vehicle_type,
            vehicle_registration_number=saved.vehicle_registration_number,
            capacity_tonnes=saved.capacity_tonnes,
            has_refrigeration=saved.has_refrigeration,
            operating_radius_km=saved.operating_radius_km,
            base_city=saved.base_city,
            base_latitude=saved.base_latitude,
            base_longitude=saved.base_longitude,
            rate_per_km_inr=saved.rate_per_km_inr,
            is_available=saved.is_available,
        )

    def find_nearby_transporters(
        self, latitude: float, longitude: float, max_radius_km: float = 100.0, min_capacity_tonnes: float = 0.0
    ) -> List[Tuple[TransporterProfileResponse, float]]:
        items = self.transport_repo.find_nearby_transporters(
            latitude=latitude,
            longitude=longitude,
            max_radius_km=max_radius_km,
            min_capacity_tonnes=min_capacity_tonnes,
        )
        return [
            (
                TransporterProfileResponse(
                    id=t.id,
                    user_id=t.user_id,
                    vehicle_type=t.vehicle_type,
                    vehicle_registration_number=t.vehicle_registration_number,
                    capacity_tonnes=t.capacity_tonnes,
                    has_refrigeration=t.has_refrigeration,
                    operating_radius_km=t.operating_radius_km,
                    base_city=t.base_city,
                    base_latitude=t.base_latitude,
                    base_longitude=t.base_longitude,
                    rate_per_km_inr=t.rate_per_km_inr,
                    is_available=t.is_available,
                ),
                dist,
            )
            for t, dist in items
        ]

    def create_request(self, requester_id: str, request: TransportRequestCreate) -> TransportRequestResponse:
        # Calculate scientific distance & initial cost estimate
        distance_km = haversine_distance_km(
            request.pickup_latitude,
            request.pickup_longitude,
            request.delivery_latitude,
            request.delivery_longitude,
        )
        estimated_cost = estimate_transport_cost_inr(
            distance_km=distance_km,
            weight_kg=request.total_weight_kg,
            requires_cold_chain=request.requires_cold_chain,
        )

        tr = TransportRequest(
            requester_id=requester_id,
            aggregation_group_id=request.aggregation_group_id,
            surplus_listing_id=request.surplus_listing_id,
            crop_id=request.crop_id,
            total_weight_kg=request.total_weight_kg,
            pickup_location=request.pickup_location,
            pickup_latitude=request.pickup_latitude,
            pickup_longitude=request.pickup_longitude,
            delivery_location=request.delivery_location,
            delivery_latitude=request.delivery_latitude,
            delivery_longitude=request.delivery_longitude,
            pickup_window_start=request.pickup_window_start,
            pickup_window_end=request.pickup_window_end,
            estimated_distance_km=distance_km,
            estimated_cost_inr=estimated_cost,
            requires_cold_chain=request.requires_cold_chain,
            status="open",
        )
        saved = self.transport_repo.create_request(tr)
        return self._build_request_response(saved)

    def get_requests(self, status: str = "open") -> List[TransportRequestResponse]:
        reqs = self.transport_repo.get_requests(status=status)
        return [self._build_request_response(r) for r in reqs]

    def create_offer(self, transporter_id: str, request: TransportOfferCreate) -> TransportOfferResponse:
        tr = self.transport_repo.get_request_by_id(request.transport_request_id)
        if not tr:
            raise EntityNotFoundException("TransportRequest", request.transport_request_id)

        offer = TransportOffer(
            transport_request_id=request.transport_request_id,
            transporter_id=transporter_id,
            vehicle_id=request.vehicle_id,
            offered_rate_total_inr=request.offered_rate_total_inr,
            pickup_datetime_proposed=request.pickup_datetime_proposed,
            estimated_delivery_datetime=request.estimated_delivery_datetime,
            status="submitted",
        )
        saved = self.transport_repo.create_offer(offer)

        # Notify requester
        self.audit_repo.create_notification(
            user_id=tr.requester_id,
            title="Transport Quote Received",
            body=f"Transporter offered ₹{offer.offered_rate_total_inr} for shipment.",
            category="transport",
            data={"offer_id": saved.id, "request_id": tr.id},
        )

        return self._build_offer_response(saved)

    def accept_transport_offer(self, requester_id: str, offer_id: str) -> ShipmentResponse:
        offer = self.transport_repo.get_offer_by_id(offer_id)
        if not offer:
            raise EntityNotFoundException("TransportOffer", offer_id)

        tr = offer.transport_request
        if tr.requester_id != requester_id:
            raise PermissionDeniedException("Only the transport requester can accept this quotation.")

        offer.status = "accepted"
        tr.status = "assigned"

        # Generate a 6-digit delivery confirmation OTP
        otp = str(random.randint(100000, 999999))

        shipment = Shipment(
            transport_request_id=tr.id,
            transport_offer_id=offer.id,
            transporter_id=offer.transporter_id,
            current_status="ASSIGNED",
            delivery_confirmation_otp=otp,
        )
        saved_shipment = self.transport_repo.create_shipment(shipment)

        return self._build_shipment_response(saved_shipment)

    def update_shipment_status(
        self, user_id: str, shipment_id: str, update: ShipmentStatusUpdate
    ) -> ShipmentResponse:
        shipment = self.transport_repo.get_shipment_by_id(shipment_id)
        if not shipment:
            raise EntityNotFoundException("Shipment", shipment_id)

        # Transporter or requester checks
        now = datetime.now(timezone.utc)
        if update.status == "PICKED_UP":
            shipment.actual_pickup_timestamp = now
        elif update.status in ["DELIVERED", "CONFIRMED"]:
            if update.delivery_confirmation_otp and shipment.delivery_confirmation_otp:
                if update.delivery_confirmation_otp != shipment.delivery_confirmation_otp:
                    raise AgriShieldException("Invalid delivery OTP.", status_code=400)
            shipment.actual_delivery_timestamp = now

        shipment = self.transport_repo.update_shipment_status(shipment, update.status, update.delivery_notes)
        return self._build_shipment_response(shipment)

    def _build_request_response(self, req: TransportRequest) -> TransportRequestResponse:
        offers = [self._build_offer_response(o) for o in req.offers]
        return TransportRequestResponse(
            id=req.id,
            requester_id=req.requester_id,
            aggregation_group_id=req.aggregation_group_id,
            surplus_listing_id=req.surplus_listing_id,
            crop_id=req.crop_id,
            crop_name=req.crop.name if req.crop else None,
            total_weight_kg=req.total_weight_kg,
            pickup_location=req.pickup_location,
            pickup_latitude=req.pickup_latitude,
            pickup_longitude=req.pickup_longitude,
            delivery_location=req.delivery_location,
            delivery_latitude=req.delivery_latitude,
            delivery_longitude=req.delivery_longitude,
            pickup_window_start=req.pickup_window_start,
            pickup_window_end=req.pickup_window_end,
            estimated_distance_km=req.estimated_distance_km,
            estimated_cost_inr=req.estimated_cost_inr,
            requires_cold_chain=req.requires_cold_chain,
            status=req.status,
            created_at=req.created_at,
            offers=offers,
        )

    def _build_offer_response(self, offer: TransportOffer) -> TransportOfferResponse:
        return TransportOfferResponse(
            id=offer.id,
            transport_request_id=offer.transport_request_id,
            transporter_id=offer.transporter_id,
            transporter_name=offer.transporter.full_name if offer.transporter else None,
            vehicle_id=offer.vehicle_id,
            vehicle_type=offer.vehicle.vehicle_type if offer.vehicle else None,
            offered_rate_total_inr=offer.offered_rate_total_inr,
            pickup_datetime_proposed=offer.pickup_datetime_proposed,
            estimated_delivery_datetime=offer.estimated_delivery_datetime,
            status=offer.status,
            created_at=offer.created_at,
        )

    def _build_shipment_response(self, s: Shipment) -> ShipmentResponse:
        return ShipmentResponse(
            id=s.id,
            transport_request_id=s.transport_request_id,
            transport_offer_id=s.transport_offer_id,
            transporter_id=s.transporter_id,
            transporter_name=s.transporter.full_name if s.transporter else None,
            actual_pickup_timestamp=s.actual_pickup_timestamp,
            actual_delivery_timestamp=s.actual_delivery_timestamp,
            current_status=s.current_status,
            delivery_notes=s.delivery_notes,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )

