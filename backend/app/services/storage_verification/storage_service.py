"""AgriShield AI - Digital Storage Verification Service

Implements tamper-evident grain batch record management, inspection logging,
and cryptographic hash chaining. Explicitly separates cryptographic record authenticity
from physical grain quality metrics.
"""

from datetime import datetime, timezone
import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    AgriShieldException,
    EntityNotFoundException,
    PermissionDeniedException,
    StorageTamperException,
)
from app.core.security import compute_sha256
from app.models.storage import StorageBatch, StorageFacility, StorageInspection, VerificationRecord
from app.repositories.crop_repository import CropRepository
from app.repositories.storage_repository import StorageRepository
from app.schemas.storage import (
    BatchVerificationSummary,
    StorageBatchCreate,
    StorageBatchResponse,
    StorageFacilityCreate,
    StorageFacilityResponse,
    StorageInspectionCreate,
    StorageInspectionResponse,
    VerificationRecordResponse,
)


class StorageService:
    def __init__(self, db: Session):
        self.db = db
        self.storage_repo = StorageRepository(db)
        self.crop_repo = CropRepository(db)

    def create_facility(self, cooperative_id: str, request: StorageFacilityCreate) -> StorageFacilityResponse:
        facility = StorageFacility(
            cooperative_id=cooperative_id,
            facility_name=request.facility_name,
            facility_type=request.facility_type,
            village=request.village,
            district=request.district,
            state=request.state,
            total_capacity_mt=request.total_capacity_mt,
            available_capacity_mt=request.total_capacity_mt,
            has_aeration=request.has_aeration,
            has_humidity_control=request.has_humidity_control,
            is_active=True,
        )
        saved = self.storage_repo.create_facility(facility)
        return self._build_facility_response(saved)

    def get_facilities(self, cooperative_id: Optional[str] = None) -> List[StorageFacilityResponse]:
        if cooperative_id:
            facilities = self.storage_repo.get_cooperative_facilities(cooperative_id)
        else:
            facilities = self.storage_repo.get_all_facilities()
        return [self._build_facility_response(f) for f in facilities]

    def register_batch(self, user_id: str, request: StorageBatchCreate) -> StorageBatchResponse:
        farmer_id = request.farmer_id or user_id
        facility = self.storage_repo.get_facility_by_id(request.facility_id)
        if not facility:
            raise EntityNotFoundException("StorageFacility", request.facility_id)

        crop = self.crop_repo.get_crop_by_id(request.crop_id)
        if not crop:
            raise EntityNotFoundException("Crop", request.crop_id)

        # Unique batch identifier
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        rand_code = uuid.uuid4().hex[:6].upper()
        batch_id_str = f"BATCH-{date_str}-{crop.name[:3].upper()}-{rand_code}"

        # Genesis cryptographic hash seal
        genesis_payload = {
            "batch_identifier": batch_id_str,
            "farmer_id": farmer_id,
            "cooperative_id": request.cooperative_id,
            "facility_id": request.facility_id,
            "crop_id": request.crop_id,
            "quantity": request.quantity,
            "unit": request.unit,
            "salt": settings.STORAGE_HASH_SALT,
        }
        genesis_hash = compute_sha256(json.dumps(genesis_payload, sort_keys=True))

        batch = StorageBatch(
            batch_identifier=batch_id_str,
            farmer_id=farmer_id,
            cooperative_id=request.cooperative_id,
            facility_id=request.facility_id,
            crop_id=request.crop_id,
            quantity=request.quantity,
            unit=request.unit,
            current_hash=genesis_hash,
            verification_status="PENDING_INSPECTION",
        )
        saved_batch = self.storage_repo.create_batch(batch)

        # Append initial Genesis Verification Record
        genesis_record = VerificationRecord(
            batch_id=saved_batch.id,
            previous_hash="0" * 64,  # Genesis block root
            record_hash=genesis_hash,
            record_authenticity_verified=True,
            inspection_completed=False,
            physical_quality_status="UNVERIFIED",
            verified_by_id=user_id,
            payload_snapshot=genesis_payload,
        )
        self.storage_repo.add_verification_record(genesis_record)

        return self._build_batch_response(saved_batch)

    def record_inspection(
        self, inspector_id: str, batch_id: str, request: StorageInspectionCreate
    ) -> StorageInspectionResponse:
        batch = self.storage_repo.get_batch_by_id(batch_id)
        if not batch:
            raise EntityNotFoundException("StorageBatch", batch_id)

        # Calculate physical quality score based on agronomic thresholds
        # Safe grain moisture is typically <= 12-14%
        quality_score = 100.0
        if request.moisture_pct > 14.0:
            quality_score -= (request.moisture_pct - 14.0) * 10.0
        if request.infestation_detected:
            quality_score -= 40.0
        quality_score -= request.foreign_matter_pct * 3.0
        quality_score = max(0.0, min(100.0, quality_score))

        # Physical produce quality assessment classification
        if quality_score >= 80.0:
            physical_status = "EXCELLENT"
        elif quality_score >= 60.0:
            physical_status = "GOOD"
        elif quality_score >= 40.0:
            physical_status = "MARGINAL"
        else:
            physical_status = "COMPROMISED"

        # Compute tamper-evident hash of inspection event
        inspection_payload = {
            "batch_id": batch.id,
            "inspector_id": inspector_id,
            "moisture_pct": request.moisture_pct,
            "temperature_c": request.temperature_c,
            "humidity_pct": request.humidity_pct,
            "infestation": request.infestation_detected,
            "quality_score": quality_score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        inspection_hash = compute_sha256(json.dumps(inspection_payload, sort_keys=True))

        inspection = StorageInspection(
            batch_id=batch.id,
            inspector_id=inspector_id,
            moisture_pct=request.moisture_pct,
            temperature_c=request.temperature_c,
            humidity_pct=request.humidity_pct,
            infestation_detected=request.infestation_detected,
            foreign_matter_pct=request.foreign_matter_pct,
            physical_quality_score=quality_score,
            physical_produce_quality_assessment=request.physical_produce_quality_assessment,
            inspector_notes=request.inspector_notes,
            inspection_hash=inspection_hash,
        )
        saved_inspection = self.storage_repo.add_inspection(inspection)

        # Cryptographic Hash Chaining: new_hash = SHA-256(previous_hash + inspection_hash)
        previous_hash = batch.current_hash
        chained_hash = compute_sha256(f"{previous_hash}:{inspection_hash}")

        batch.current_hash = chained_hash
        batch.verification_status = "VERIFIED" if quality_score >= 50.0 else "REJECTED"
        self.storage_repo.update_batch(batch)

        # Append-only Verification Audit Record
        audit_record = VerificationRecord(
            batch_id=batch.id,
            previous_hash=previous_hash,
            record_hash=chained_hash,
            record_authenticity_verified=True,
            inspection_completed=True,
            physical_quality_status=physical_status,
            verified_by_id=inspector_id,
            payload_snapshot=inspection_payload,
        )
        self.storage_repo.add_verification_record(audit_record)

        return self._build_inspection_response(saved_inspection)

    def verify_batch_integrity(self, batch_id: str) -> BatchVerificationSummary:
        """Cryptographically audits the entire hash chain of a batch from genesis to present,

        and compiles latest physical produce quality readings.
        """
        batch = self.storage_repo.get_batch_by_id(batch_id)
        if not batch:
            raise EntityNotFoundException("StorageBatch", batch_id)

        records = self.storage_repo.get_verification_records(batch.id)
        inspections = self.storage_repo.get_inspections_for_batch(batch.id)

        # Audit hash chain
        chain_valid = True
        if not records:
            chain_valid = False
        else:
            prev = "0" * 64
            for r in records:
                if r.previous_hash != prev:
                    chain_valid = False
                    break
                prev = r.record_hash

            if prev != batch.current_hash:
                chain_valid = False

        latest_inspection = inspections[0] if inspections else None
        latest_record = records[-1] if records else None

        return BatchVerificationSummary(
            batch_identifier=batch.batch_identifier,
            record_authenticity=chain_valid,
            cryptographic_seal_valid=chain_valid,
            current_hash=batch.current_hash,
            inspection_completed=bool(inspections),
            total_inspections=len(inspections),
            latest_inspection_date=latest_inspection.inspection_timestamp if latest_inspection else None,
            physical_quality_status=latest_record.physical_quality_status if latest_record else "UNVERIFIED",
            moisture_pct=latest_inspection.moisture_pct if latest_inspection else None,
            infestation_detected=latest_inspection.infestation_detected if latest_inspection else None,
        )

    def get_batches(
        self, farmer_id: Optional[str] = None, cooperative_id: Optional[str] = None
    ) -> List[StorageBatchResponse]:
        batches = self.storage_repo.get_batches(farmer_id=farmer_id, cooperative_id=cooperative_id)
        return [self._build_batch_response(b) for b in batches]

    def get_batch(self, batch_id: str) -> StorageBatchResponse:
        batch = self.storage_repo.get_batch_by_id(batch_id)
        if not batch:
            raise EntityNotFoundException("StorageBatch", batch_id)
        return self._build_batch_response(batch)

    def _build_facility_response(self, f: StorageFacility) -> StorageFacilityResponse:
        return StorageFacilityResponse(
            id=f.id,
            cooperative_id=f.cooperative_id,
            facility_name=f.facility_name,
            facility_type=f.facility_type,
            village=f.village,
            district=f.district,
            state=f.state,
            total_capacity_mt=f.total_capacity_mt,
            available_capacity_mt=f.available_capacity_mt,
            has_aeration=f.has_aeration,
            has_humidity_control=f.has_humidity_control,
            is_active=f.is_active,
        )

    def _build_inspection_response(self, insp: StorageInspection) -> StorageInspectionResponse:
        return StorageInspectionResponse(
            id=insp.id,
            batch_id=insp.batch_id,
            inspector_id=insp.inspector_id,
            inspector_name=insp.inspector.full_name if insp.inspector else None,
            inspection_timestamp=insp.inspection_timestamp,
            moisture_pct=insp.moisture_pct,
            temperature_c=insp.temperature_c,
            humidity_pct=insp.humidity_pct,
            infestation_detected=insp.infestation_detected,
            foreign_matter_pct=insp.foreign_matter_pct,
            physical_quality_score=insp.physical_quality_score,
            physical_produce_quality_assessment=insp.physical_produce_quality_assessment,
            inspector_notes=insp.inspector_notes,
            inspection_hash=insp.inspection_hash,
        )

    def _build_batch_response(self, b: StorageBatch) -> StorageBatchResponse:
        inspections_resp = [self._build_inspection_response(i) for i in b.inspections]
        records_resp = [
            VerificationRecordResponse(
                id=vr.id,
                batch_id=vr.batch_id,
                previous_hash=vr.previous_hash,
                record_hash=vr.record_hash,
                record_authenticity_verified=vr.record_authenticity_verified,
                inspection_completed=vr.inspection_completed,
                physical_quality_status=vr.physical_quality_status,
                verified_by_id=vr.verified_by_id,
                timestamp=vr.timestamp,
                payload_snapshot=vr.payload_snapshot,
            )
            for vr in b.verification_records
        ]

        return StorageBatchResponse(
            id=b.id,
            batch_identifier=b.batch_identifier,
            farmer_id=b.farmer_id,
            farmer_name=b.farmer.full_name if b.farmer else None,
            cooperative_id=b.cooperative_id,
            cooperative_name=b.cooperative.full_name if b.cooperative else None,
            facility_id=b.facility_id,
            facility_name=b.facility.facility_name if b.facility else None,
            crop_id=b.crop_id,
            crop_name=b.crop.name if b.crop else None,
            quantity=b.quantity,
            unit=b.unit,
            registration_timestamp=b.registration_timestamp,
            current_hash=b.current_hash,
            verification_status=b.verification_status,
            created_at=b.created_at,
            inspections=inspections_resp,
            verification_records=records_resp,
        )

