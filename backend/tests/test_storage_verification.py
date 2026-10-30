"""AgriShield AI - Digital Storage Verification Integration Tests
"""

import pytest


def test_storage_batch_inspection_and_cryptographic_verification(
    client, farmer_token, coop_token, seed_test_users_and_crops
):
    crop = seed_test_users_and_crops["crops"]["wheat"]
    coop_user = seed_test_users_and_crops["coop_admin"]

    # 1. Cooperative creates storage facility
    fac_res = client.post(
        "/api/v1/cooperatives/facilities",
        json={
            "facility_name": "Junnar Taluka Sahakari Godown #3",
            "facility_type": "ventilated_godown",
            "village": "Otur",
            "district": "Pune",
            "state": "Maharashtra",
            "total_capacity_mt": 500.0,
            "has_aeration": True,
            "has_humidity_control": False,
        },
        headers=coop_token,
    )
    assert fac_res.status_code == 201
    facility_id = fac_res.json()["id"]

    # 2. Farmer registers wheat batch
    batch_res = client.post(
        "/api/v1/storage/batches",
        json={
            "cooperative_id": coop_user.id,
            "facility_id": facility_id,
            "crop_id": crop.id,
            "quantity": 4500.0,
            "unit": "kg",
        },
        headers=farmer_token,
    )
    assert batch_res.status_code == 201
    batch_data = batch_res.json()
    batch_id = batch_data["id"]
    genesis_hash = batch_data["current_hash"]
    assert batch_data["batch_identifier"].startswith("BATCH-")
    assert batch_data["verification_status"] == "PENDING_INSPECTION"
    assert len(genesis_hash) == 64

    # 3. Cooperative inspector records official inspection
    insp_res = client.post(
        f"/api/v1/storage/batches/{batch_id}/inspect",
        json={
            "moisture_pct": 11.8,  # Ideal safe moisture for wheat (<=12%)
            "temperature_c": 22.5,
            "humidity_pct": 58.0,
            "infestation_detected": False,
            "foreign_matter_pct": 0.5,
            "physical_produce_quality_assessment": "Grain is dry, sound, free from weevils, suitable for 9-month warehousing.",
            "inspector_notes": "Sample drawn from 10 distinct bags using standard sampling probe.",
        },
        headers=coop_token,
    )
    assert insp_res.status_code == 201
    insp_data = insp_res.json()
    assert insp_data["physical_quality_score"] >= 90.0

    # 4. Audit cryptographic verification record
    verify_res = client.get(f"/api/v1/storage/batches/{batch_id}/verification")
    assert verify_res.status_code == 200
    audit = verify_res.json()

    # Assert explicit separation of concepts:
    # 1. Record authenticity (cryptographic proof)
    assert audit["record_authenticity"] is True
    assert audit["cryptographic_seal_valid"] is True
    # 2. Inspection completion
    assert audit["inspection_completed"] is True
    assert audit["total_inspections"] == 1
    # 3. Physical produce quality
    assert audit["physical_quality_status"] == "EXCELLENT"
    assert audit["moisture_pct"] == 11.8
    assert audit["infestation_detected"] is False
    assert "Cryptographic proof guarantees digital record immutability" in audit["disclaimer"]

