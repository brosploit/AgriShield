"""AgriShield AI - Transportation & Shipments Integration Tests
"""

from datetime import datetime, timedelta, timezone


def test_transport_flow(
    client, farmer_token, transporter_token, seed_test_users_and_crops
):
    crop = seed_test_users_and_crops["crops"]["tomato"]

    # 1. Transporter registers profile
    transporter_res = client.post(
        "/api/v1/transporters/register",
        json={
            "vehicle_type": "Tata 407 Tempo",
            "vehicle_registration_number": "MH-14-GH-4421",
            "capacity_tonnes": 3.5,
            "has_refrigeration": False,
            "operating_radius_km": 150.0,
            "base_city": "Pune",
            "base_latitude": 18.5204,
            "base_longitude": 73.8567,
            "rate_per_km_inr": 28.0,
        },
        headers=transporter_token,
    )
    assert transporter_res.status_code == 201

    # 2. Farmer creates Transport Request (Narayangaon -> Pune Market Yard, approx 75 km)
    now = datetime.now(timezone.utc)
    req_res = client.post(
        "/api/v1/transport/requests",
        json={
            "crop_id": crop.id,
            "total_weight_kg": 2500.0,
            "pickup_location": "Narayangaon Farmer Market",
            "pickup_latitude": 19.1245,
            "pickup_longitude": 73.9782,
            "delivery_location": "Gultekdi Market Yard, Pune",
            "delivery_latitude": 18.4975,
            "delivery_longitude": 73.8690,
            "pickup_window_start": (now + timedelta(hours=4)).isoformat(),
            "pickup_window_end": (now + timedelta(hours=10)).isoformat(),
            "requires_cold_chain": False,
        },
        headers=farmer_token,
    )
    assert req_res.status_code == 201
    request_data = req_res.json()
    assert request_data["estimated_distance_km"] > 60.0
    assert request_data["estimated_cost_inr"] > 1500.0
    request_id = request_data["id"]

    # 3. Transporter submits an offer
    offer_res = client.post(
        "/api/v1/transport/offers",
        json={
            "transport_request_id": request_id,
            "offered_rate_total_inr": 2800.0,
            "pickup_datetime_proposed": (now + timedelta(hours=5)).isoformat(),
            "estimated_delivery_datetime": (now + timedelta(hours=9)).isoformat(),
        },
        headers=transporter_token,
    )
    assert offer_res.status_code == 201
    offer_id = offer_res.json()["id"]

    # 4. Requester accepts offer -> shipment created
    shipment_res = client.post(f"/api/v1/transport/offers/{offer_id}/accept", headers=farmer_token)
    assert shipment_res.status_code == 200
    shipment = shipment_res.json()
    assert shipment["current_status"] == "ASSIGNED"
    shipment_id = shipment["id"]

    # 5. Transporter marks in-transit
    update_res = client.patch(
        f"/api/v1/transport/shipments/{shipment_id}/status",
        json={"status": "IN_TRANSIT", "delivery_notes": "Departed Narayangaon via NH60"},
        headers=transporter_token,
    )
    assert update_res.status_code == 200
    assert update_res.json()["current_status"] == "IN_TRANSIT"

