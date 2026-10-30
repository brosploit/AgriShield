"""AgriShield AI - Freshness Intelligence Integration Tests
"""

from datetime import datetime, timezone


def test_assess_freshness_optimal_conditions(client, farmer_token, seed_test_users_and_crops):
    crop = seed_test_users_and_crops["crops"]["tomato"]
    payload = {
        "crop_id": crop.id,
        "harvest_datetime": datetime.now(timezone.utc).isoformat(),
        "current_temperature_c": 15.0,  # Optimal for tomato (13 - 18)
        "current_humidity_pct": 90.0,   # Optimal for tomato (85 - 95)
        "storage_type": "cold_storage",
        "storage_duration_hours": 12.0,
        "transportation_conditions": "refrigerated",
        "crop_quantity_kg": 500.0,
    }
    response = client.post("/api/v1/freshness/assess", json=payload, headers=farmer_token)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_category"] == "Low"
    assert data["risk_score"] < 25.0
    assert "Optimal holding temperature" in data["influencing_factors"]["temperature"]


def test_assess_freshness_severe_heat_stress(client, farmer_token, seed_test_users_and_crops):
    crop = seed_test_users_and_crops["crops"]["tomato"]
    payload = {
        "crop_id": crop.id,
        "harvest_datetime": datetime.now(timezone.utc).isoformat(),
        "current_temperature_c": 38.0,  # High heat stress > 30C
        "current_humidity_pct": 40.0,   # Low humidity -> desiccation
        "storage_type": "open_air",
        "storage_duration_hours": 72.0,
        "transportation_conditions": "ambient_open",
        "crop_quantity_kg": 200.0,
    }
    response = client.post("/api/v1/freshness/assess", json=payload, headers=farmer_token)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 65.0
    assert data["risk_category"] in ["High", "Critical"]
    assert "Immediate" in data["estimated_urgency"] or "Urgent" in data["estimated_urgency"]


def test_get_freshness_history(client, farmer_token, seed_test_users_and_crops):
    # Ensure at least one assessment exists
    crop = seed_test_users_and_crops["crops"]["tomato"]
    client.post(
        "/api/v1/freshness/assess",
        json={
            "crop_id": crop.id,
            "harvest_datetime": datetime.now(timezone.utc).isoformat(),
            "current_temperature_c": 22.0,
            "current_humidity_pct": 80.0,
            "storage_type": "ventilated_godown",
            "storage_duration_hours": 24.0,
            "crop_quantity_kg": 300.0,
        },
        headers=farmer_token,
    )
    response = client.get("/api/v1/freshness/history", headers=farmer_token)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["crop_name"] == "Tomato"


def test_get_crop_guidelines(client):
    response = client.get("/api/v1/freshness/crop-guidelines")
    assert response.status_code == 200
    data = response.json()
    assert "tomato" in data["supported_crops"]
    assert "wheat" in data["supported_crops"]

