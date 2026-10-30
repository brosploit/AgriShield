"""AgriShield AI - Unified Recommendations Integration Tests
"""

from datetime import datetime, timezone


def test_unified_recommendation_generation(
    client, farmer_token, seed_test_users_and_crops
):
    crop = seed_test_users_and_crops["crops"]["tomato"]

    # 1. Trigger severe deterioration assessment on Tomato (heat 38C)
    client.post(
        "/api/v1/freshness/assess",
        json={
            "crop_id": crop.id,
            "harvest_datetime": datetime.now(timezone.utc).isoformat(),
            "current_temperature_c": 38.0,
            "current_humidity_pct": 35.0,
            "storage_type": "open_air",
            "storage_duration_hours": 48.0,
            "crop_quantity_kg": 800.0,
        },
        headers=farmer_token,
    )

    # 2. Register surplus of 800 kg (sub-truckload)
    client.post(
        "/api/v1/surplus/register",
        json={
            "crop_id": crop.id,
            "quantity_kg": 800.0,
            "quality_grade": "Grade B",
            "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
            "expected_price_per_kg": 20.0,
            "village": "Narayangaon",
            "district": "Pune",
            "latitude": 19.1245,
            "longitude": 73.9782,
        },
        headers=farmer_token,
    )

    # 3. Generate recommendations
    gen_res = client.post(
        "/api/v1/recommendations/generate",
        json={"include_all_crops": True},
        headers=farmer_token,
    )
    assert gen_res.status_code == 201
    recs = gen_res.json()
    assert len(recs) >= 1

    categories = [r["category"] for r in recs]
    assert "URGENT_SALE" in categories or "SURPLUS_AGGREGATION" in categories

    first_rec = recs[0]
    rec_id = first_rec["id"]
    get_res = client.get(f"/api/v1/recommendations/{rec_id}")
    assert get_res.status_code == 200
    assert get_res.json()["priority"] in ["CRITICAL", "HIGH", "MEDIUM"]
    assert len(get_res.json()["suggested_action"]) > 10

