"""AgriShield AI - Digital Storage Verification Repository

Implements storage facility management, batch records, inspections, and cryptographic verification chaining.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.storage import StorageFacility, StorageBatch, StorageInspection, VerificationRecord


class StorageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_facility(self, facility: StorageFacility) -> StorageFacility:
        self.db.add(facility)
        self.db.commit()
        self.db.refresh(facility)
        return facility

    def get_facility_by_id(self, facility_id: str) -> Optional[StorageFacility]:
        return self.db.query(StorageFacility).filter(StorageFacility.id == facility_id).first()

    def get_cooperative_facilities(self, cooperative_id: str) -> List[StorageFacility]:
        return self.db.query(StorageFacility).filter(StorageFacility.cooperative_id == cooperative_id).all()

    def get_all_facilities(self) -> List[StorageFacility]:
        return self.db.query(StorageFacility).filter(StorageFacility.is_active.is_(True)).all()

    def create_batch(self, batch: StorageBatch) -> StorageBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_batch_by_id(self, batch_id: str) -> Optional[StorageBatch]:
        return self.db.query(StorageBatch).filter(StorageBatch.id == batch_id).first()

    def get_batch_by_identifier(self, identifier: str) -> Optional[StorageBatch]:
        return self.db.query(StorageBatch).filter(StorageBatch.batch_identifier == identifier).first()

    def get_batches(
        self, farmer_id: Optional[str] = None, cooperative_id: Optional[str] = None, limit: int = 50
    ) -> List[StorageBatch]:
        query = self.db.query(StorageBatch)
        if farmer_id:
            query = query.filter(StorageBatch.farmer_id == farmer_id)
        if cooperative_id:
            query = query.filter(StorageBatch.cooperative_id == cooperative_id)
        return query.order_by(StorageBatch.created_at.desc()).limit(limit).all()

    def update_batch(self, batch: StorageBatch) -> StorageBatch:
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def add_inspection(self, inspection: StorageInspection) -> StorageInspection:
        self.db.add(inspection)
        self.db.commit()
        self.db.refresh(inspection)
        return inspection

    def get_inspections_for_batch(self, batch_id: str) -> List[StorageInspection]:
        return (
            self.db.query(StorageInspection)
            .filter(StorageInspection.batch_id == batch_id)
            .order_by(StorageInspection.inspection_timestamp.desc())
            .all()
        )

    def add_verification_record(self, record: VerificationRecord) -> VerificationRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_verification_records(self, batch_id: str) -> List[VerificationRecord]:
        return (
            self.db.query(VerificationRecord)
            .filter(VerificationRecord.batch_id == batch_id)
            .order_by(VerificationRecord.timestamp.asc())
            .all()
        )

