"""AgriShield AI - Buyer Marketplace & Offers Integration Tests
"""

from datetime import datetime, timedelta, timezone


def test_buyer_requirement_lifecycle(client, buyer_token, seed_test_users_and_crops):
    crop = seed_test_users_and_crops["crops"]["tomato"]
    deadline = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    payload = {
        "crop_id": crop.id,
        "required_quantity_kg": 5000.0,
        "quality_grade_requirement": "Grade A",
        "target_price_per_kg": 27.0,
        "delivery_location": "Market Yard, Gultekdi, Pune",
        "delivery_district": "Pune",
        "delivery_deadline": deadline,
    }
    create_res = client.post("/api/v1/buyers/requirements", json=payload, headers=buyer_token)
    assert create_res.status_code == 201
    req_id = create_res.json()["id"]

    # Query requirements
    get_res = client.get(f"/api/v1/buyers/requirements/{req_id}")
    assert get_res.status_code == 200
    assert get_res.json()["target_price_per_kg"] == 27.0


def test_offer_creation_and_authorization(
    client, farmer_token, buyer_token, seed_test_users_and_crops
):
    crop = seed_test_users_and_crops["crops"]["tomato"]

    # Farmer registers surplus
    listing_res = client.post(
        "/api/v1/surplus/register",
        json={
            "crop_id": crop.id,
            "quantity_kg": 2000.0,
            "quality_grade": "Grade A",
            "harvest_timestamp": datetime.now(timezone.utc).isoformat(),
            "expected_price_per_kg": 25.0,
            "village": "Manchar",
            "district": "Pune",
            "latitude": 19.0021,
            "longitude": 73.9421,
        },
        headers=farmer_token,
    )
    listing_id = listing_res.json()["id"]

    # Buyer creates an offer of Rs 26/kg for 1500 kg
    valid_until = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    offer_res = client.post(
        "/api/v1/offers",
        json={
            "surplus_listing_id": listing_id,
            "offered_price_per_kg": 26.0,
            "offered_quantity_kg": 1500.0,
            "terms": "Net 2 days on mandi weighment",
            "valid_until": valid_until,
        },
        headers=buyer_token,
    )
    assert offer_res.status_code == 201
    offer_id = offer_res.json()["id"]
    assert offer_res.json()["total_amount_inr"] == 39000.0

    # Unauthorized accept attempt: Buyer attempting to accept own offer should fail with 403
    unauth_accept = client.patch(
        f"/api/v1/offers/{offer_id}/status",
        json={"status": "accepted"},
        headers=buyer_token,
    )
    assert unauth_accept.status_code == 403

    # Authorized accept: Farmer who owns the listing accepts the offer
    auth_accept = client.patch(
        f"/api/v1/offers/{offer_id}/status",
        json={"status": "accepted"},
        headers=farmer_token,
    )
    assert auth_accept.status_code == 200
    assert auth_accept.json()["status"] == "accepted"

