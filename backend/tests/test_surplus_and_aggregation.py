"""AgriShield AI - Surplus & Smart Aggregation Integration Tests
"""

from datetime import datetime, timedelta, timezone


def test_register_and_query_surplus(client, farmer_token, seed_test_users_and_crops):
    crop = seed_test_users_and_crops["crops"]["tomato"]
    payload = {
        "crop_id": crop.id,
        "quantity_kg": 1500.0,
        "quality_grade": "Grade A",
        "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
        "expected_price_per_kg": 24.50,
        "village": "Alephata",
        "district": "Pune",
        "state": "Maharashtra",
        "latitude": 19.1834,
        "longitude": 74.1032,
    }
    response = client.post("/api/v1/surplus/register", json=payload, headers=farmer_token)
    assert response.status_code == 201
    listing = response.json()
    assert listing["initial_quantity_kg"] == 1500.0
    assert listing["available_quantity_kg"] == 1500.0
    assert listing["status"] == "active"

    # Query listings
    list_res = client.get("/api/v1/surplus/listings")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


def test_nearby_surplus_discovery(client, farmer_token, seed_test_users_and_crops):
    crop = seed_test_users_and_crops["crops"]["tomato"]
    # Register surplus at Narayangaon (19.1245, 73.9782)
    client.post(
        "/api/v1/surplus/register",
        json={
            "crop_id": crop.id,
            "quantity_kg": 1000.0,
            "quality_grade": "Grade A",
            "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
            "expected_price_per_kg": 25.0,
            "village": "Narayangaon",
            "district": "Pune",
            "latitude": 19.1245,
            "longitude": 73.9782,
        },
        headers=farmer_token,
    )

    # Search from nearby Junnar (19.2065, 73.8767) - approx 14 km
    res = client.get("/api/v1/surplus/nearby?latitude=19.2065&longitude=73.8767&max_radius_km=30")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    assert items[0]["distance_km"] <= 30.0


def test_aggregation_group_workflow_and_double_allocation_prevention(
    client, farmer_token, seed_test_users_and_crops
):
    crop = seed_test_users_and_crops["crops"]["tomato"]

    # 1. Register a surplus lot of 1000 kg
    reg_res = client.post(
        "/api/v1/surplus/register",
        json={
            "crop_id": crop.id,
            "quantity_kg": 1000.0,
            "quality_grade": "Grade A",
            "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
            "expected_price_per_kg": 25.0,
            "village": "Narayangaon",
            "district": "Pune",
            "latitude": 19.1245,
            "longitude": 73.9782,
        },
        headers=farmer_token,
    )
    listing_id = reg_res.json()["id"]

    # 2. Create Aggregation Group for 3000 kg target
    expiry = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    group_res = client.post(
        "/api/v1/aggregation/create",
        json={
            "crop_id": crop.id,
            "target_quantity_kg": 3000.0,
            "target_price_per_kg": 26.0,
            "hub_village": "Narayangaon",
            "hub_district": "Pune",
            "hub_latitude": 19.1245,
            "hub_longitude": 73.9782,
            "max_distance_radius_km": 25.0,
            "expiry_timestamp": expiry,
        },
        headers=farmer_token,
    )
    assert group_res.status_code == 201
    group_id = group_res.json()["id"]

    # 3. Join group with 600 kg commitment
    join_res = client.post(
        f"/api/v1/aggregation/{group_id}/join",
        json={"surplus_listing_id": listing_id, "committed_quantity_kg": 600.0},
        headers=farmer_token,
    )
    assert join_res.status_code == 200
    group_data = join_res.json()
    assert group_data["current_quantity_kg"] == 600.0

    # Verify listing available quantity decremented to 400 kg
    check_listing = client.get(f"/api/v1/surplus/{listing_id}").json()
    assert check_listing["available_quantity_kg"] == 400.0

    # 4. Attempt to allocate 500 kg (Double Allocation Prevention Check)
    excess_res = client.post(
        f"/api/v1/aggregation/{group_id}/join",
        json={"surplus_listing_id": listing_id, "committed_quantity_kg": 500.0},
        headers=farmer_token,
    )
    # Must fail with 409 Conflict due to insufficient quantity
    assert excess_res.status_code == 409
    assert "exceeds available" in excess_res.json()["message"]

    # 5. Leave group -> releases 600 kg back to available quantity
    leave_res = client.post(f"/api/v1/aggregation/{group_id}/leave", headers=farmer_token)
    assert leave_res.status_code == 200
    restored_listing = client.get(f"/api/v1/surplus/{listing_id}").json()
    assert restored_listing["available_quantity_kg"] == 1000.0

