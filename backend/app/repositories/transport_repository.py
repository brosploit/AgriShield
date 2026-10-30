"""AgriShield AI - Transport Repository
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.transport import TransportRequest, TransportOffer, Shipment
from app.models.user import TransporterProfile
from app.utils.geo import haversine_distance_km


class TransportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_request(self, req: TransportRequest) -> TransportRequest:
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def get_request_by_id(self, req_id: str) -> Optional[TransportRequest]:
        return self.db.query(TransportRequest).filter(TransportRequest.id == req_id).first()

    def get_requests(self, status: str = "open", limit: int = 50) -> List[TransportRequest]:
        return (
            self.db.query(TransportRequest)
            .filter(TransportRequest.status == status)
            .order_by(TransportRequest.created_at.desc())
            .limit(limit)
            .all()
        )

    def create_offer(self, offer: TransportOffer) -> TransportOffer:
        self.db.add(offer)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def get_offer_by_id(self, offer_id: str) -> Optional[TransportOffer]:
        return self.db.query(TransportOffer).filter(TransportOffer.id == offer_id).first()

    def create_shipment(self, shipment: Shipment) -> Shipment:
        self.db.add(shipment)
        self.db.commit()
        self.db.refresh(shipment)
        return shipment

    def get_shipment_by_id(self, shipment_id: str) -> Optional[Shipment]:
        return self.db.query(Shipment).filter(Shipment.id == shipment_id).first()

    def update_shipment_status(self, shipment: Shipment, new_status: str, notes: Optional[str] = None) -> Shipment:
        shipment.current_status = new_status
        if notes:
            shipment.delivery_notes = notes
        self.db.commit()
        self.db.refresh(shipment)
        return shipment

    def find_nearby_transporters(
        self, latitude: float, longitude: float, max_radius_km: float = 100.0, min_capacity_tonnes: float = 0.0
    ) -> List[Tuple[TransporterProfile, float]]:
        transporters = (
            self.db.query(TransporterProfile)
            .filter(
                TransporterProfile.is_available.is_(True),
                TransporterProfile.capacity_tonnes >= min_capacity_tonnes,
                TransporterProfile.base_latitude.isnot(None),
                TransporterProfile.base_longitude.isnot(None),
            )
            .all()
        )

        results = []
        for t in transporters:
            dist = haversine_distance_km(latitude, longitude, t.base_latitude, t.base_longitude)
            if dist <= max_radius_km and dist <= t.operating_radius_km:
                results.append((t, dist))

        results.sort(key=lambda x: x[1])
        return results
