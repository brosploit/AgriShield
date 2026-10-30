"""AgriShield AI - Transportation & Shipment API Endpoints
"""

from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.core.permissions import UserRole
from app.models.user import User
from app.schemas.transport import (
    ShipmentResponse,
    ShipmentStatusUpdate,
    TransportOfferCreate,
    TransportOfferResponse,
    TransportRequestCreate,
    TransportRequestResponse,
)
from app.schemas.user import TransporterProfileCreate, TransporterProfileResponse
from app.services.transport_service import TransportService

router = APIRouter(tags=["Transportation"])


@router.post(
    "/transporters/register",
    response_model=TransporterProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.TRANSPORTER]))],
)
def register_transporter(
    profile_data: TransporterProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = TransportService(db)
    return service.register_transporter(current_user.id, profile_data)


@router.get("/transporters/nearby")
def get_nearby_transporters(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    max_radius_km: float = Query(default=100.0, gt=0.0),
    min_capacity_tonnes: float = Query(default=0.0, ge=0.0),
    db: Session = Depends(get_db),
):
    service = TransportService(db)
    items = service.find_nearby_transporters(
        latitude=latitude,
        longitude=longitude,
        max_radius_km=max_radius_km,
        min_capacity_tonnes=min_capacity_tonnes,
    )
    return [
        {
            "transporter": item[0].model_dump(),
            "distance_km": item[1],
            "is_estimated_distance": True,
        }
        for item in items
    ]


@router.post(
    "/transport/requests",
    response_model=TransportRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transport_request(
    request_data: TransportRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = TransportService(db)
    return service.create_request(current_user.id, request_data)


@router.get("/transport/requests", response_model=List[TransportRequestResponse])
def get_transport_requests(status: str = "open", db: Session = Depends(get_db)):
    service = TransportService(db)
    return service.get_requests(status=status)


@router.post(
    "/transport/offers",
    response_model=TransportOfferResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.TRANSPORTER]))],
)
def create_transport_offer(
    offer_data: TransportOfferCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = TransportService(db)
    return service.create_offer(current_user.id, offer_data)


@router.post("/transport/offers/{offer_id}/accept", response_model=ShipmentResponse)
def accept_transport_offer(
    offer_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = TransportService(db)
    return service.accept_transport_offer(current_user.id, offer_id)


@router.patch("/transport/shipments/{shipment_id}/status", response_model=ShipmentResponse)
def update_shipment_status(
    shipment_id: str,
    update: ShipmentStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = TransportService(db)
    return service.update_shipment_status(current_user.id, shipment_id, update)

