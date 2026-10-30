"""AgriShield AI - Authentication & Authorization Integration Tests
"""

import pytest


def test_user_registration_success(client):
    payload = {
        "email": "new.farmer@agrishield.internal",
        "phone_number": "+919988776655",
        "password": "SecurePassword123!",
        "full_name": "Suresh Shinde",
        "role": "farmer",
        "village": "Manchar",
        "district": "Pune",
        "state": "Maharashtra",
        "pincode": "410503",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "farmer"
    assert "password" not in data
    assert "hashed_password" not in data


def test_user_registration_duplicate_email(client, seed_test_users_and_crops):
    payload = {
        "email": "farmer.test@agrishield.internal",  # Already exists
        "phone_number": "+919999999999",
        "password": "Password123!",
        "full_name": "Duplicate User",
        "role": "farmer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_user_login_success(client, seed_test_users_and_crops):
    payload = {
        "identifier": "farmer.test@agrishield.internal",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "farmer"


def test_user_login_invalid_password(client, seed_test_users_and_crops):
    payload = {
        "identifier": "farmer.test@agrishield.internal",
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_token_refresh_and_rotation(client, seed_test_users_and_crops):
    # 1. Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"identifier": "farmer.test@agrishield.internal", "password": "Password123!"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # 2. Refresh
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    new_refresh_token = new_data["refresh_token"]
    assert new_refresh_token != refresh_token

    # 3. Old refresh token should now be revoked
    stale_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert stale_res.status_code == 401


def test_auth_me_protected_endpoint(client, farmer_token):
    response = client.get("/api/v1/auth/me", headers=farmer_token)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "farmer.test@agrishield.internal"


def test_protected_endpoint_without_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

