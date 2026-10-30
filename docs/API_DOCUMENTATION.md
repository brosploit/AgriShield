# AgriShield AI — REST API Documentation (v1.0.0)

All core endpoints are prefixed with `/api/v1` and accessible via HTTP/JSON. Complete interactive documentation is accessible at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **System Health:** `http://localhost:8000/health`

---

## 1. Authentication & Session Endpoints

### 1.1 User Registration
- **Endpoint:** `POST /api/v1/auth/register`
- **Access:** Public (Rate limited to 10 req/min)
- **Status:** `201 Created`

**Request Payload:**
```json
{
  "email": "farmer.rajesh@agrishield.internal",
  "phone_number": "+919876543210",
  "password": "SecurePassword123!",
  "full_name": "Rajesh Patil",
  "role": "farmer",
  "village": "Narayangaon",
  "district": "Pune",
  "state": "Maharashtra",
  "pincode": "410504",
  "latitude": 19.1245,
  "longitude": 73.9782
}
```

### 1.2 User Login
- **Endpoint:** `POST /api/v1/auth/login`
- **Status:** `200 OK`

**Response Payload:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": "usr-8a91b2c3",
  "role": "farmer"
}
```

### 1.3 Refresh Token Rotation
- **Endpoint:** `POST /api/v1/auth/refresh`
- **Status:** `200 OK`
- **Note:** Stale refresh tokens are immediately revoked upon successful rotation.

---

## 2. AI Freshness Intelligence Endpoints

### 2.1 Assess Crop Degradation
- **Endpoint:** `POST /api/v1/freshness/assess`
- **Access:** Requires `Bearer` token (`farmer` or `cooperative_admin`)
- **Status:** `200 OK`

**Request Payload:**
```json
{
  "crop_name": "Tomato",
  "harvest_datetime": "2026-10-28T06:00:00Z",
  "current_temperature_c": 31.5,
  "current_humidity_pct": 58.0,
  "storage_type": "traditional_shed",
  "storage_duration_hours": 48.0,
  "transportation_conditions": "ambient_open",
  "crop_quantity_kg": 1200.0
}
```

**Response Payload:**
```json
{
  "id": "asm-9812a7",
  "farmer_id": "usr-8a91b2c3",
  "crop_id": "crp-tomato-01",
  "crop_name": "Tomato",
  "risk_score": 68.4,
  "risk_category": "High",
  "estimated_urgency": "HIGH",
  "recommended_action": "SURPLUS_AGGREGATION: Accelerating degradation at 2.4x baseline. Divert to fast-sale lot or refrigerated cold storage within 36 hours.",
  "influencing_factors": {
    "q10_thermal_factor": 2.41,
    "vpd_vapor_pressure_deficit_kpa": 1.94,
    "storage_facility_factor": 1.15,
    "effective_elapsed_hours": 133.2
  },
  "model_version": "1.0.0-randomforest-r2-0.98",
  "confidence_score": 0.94,
  "assessment_timestamp": "2026-10-30T10:15:00Z"
}
```

### 2.2 Crop Guidelines Directory
- **Endpoint:** `GET /api/v1/freshness/crop-guidelines`
- **Access:** Public / Authenticated
- **Description:** Returns optimal thermal thresholds, humidity envelopes, and post-harvest care protocols for all tracked crop categories.

---

## 3. Surplus & Smart Aggregation Endpoints

### 3.1 Register Crop Surplus
- **Endpoint:** `POST /api/v1/surplus/listings`
- **Access:** `farmer`
- **Description:** Publishes available sub-truckload surplus produce into the regional pool.

### 3.2 Discover Nearby Surplus Lots
- **Endpoint:** `GET /api/v1/surplus/nearby?crop_name=Tomato&radius_km=25`
- **Access:** `farmer`, `buyer`, `cooperative_admin`
- **Description:** Executes spatial Haversine bounding-box queries to locate complementary crop listings suitable for joint bulk transit.

### 3.3 Create Aggregation Group
- **Endpoint:** `POST /api/v1/aggregation/groups`
- **Access:** `farmer`, `cooperative_admin`
- **Concurrency Protection:** Uses `with_for_update` row locks on member listings to prevent multi-group allocation conflicts.

---

## 4. Transportation & Logistics Endpoints

### 4.1 Request Haulage Quote
- **Endpoint:** `POST /api/v1/transporters/requests`
- **Access:** `farmer`, `buyer`

**Request Payload:**
```json
{
  "origin_latitude": 19.9975,
  "origin_longitude": 73.7898,
  "destination_latitude": 19.0760,
  "destination_longitude": 72.8777,
  "crop_name": "Tomato",
  "weight_tons": 10.0,
  "refrigeration_required": true,
  "scheduled_pickup_time": "2026-10-31T05:00:00Z"
}
```

**Response Payload:**
```json
{
  "request_id": "trq-5502a",
  "calculated_distance_km": 168.0,
  "estimated_transit_hours": 4.0,
  "estimated_cost_inr": 7056.0,
  "status": "pending_offers"
}
```

### 4.2 Verify Delivery via OTP
- **Endpoint:** `POST /api/v1/transporters/shipments/{shipment_id}/confirm-delivery`
- **Access:** `farmer`, `buyer`, `transporter`
- **Payload:** `{"confirmation_otp": "849201"}`
- **Description:** Atomically verifies the 6-digit confirmation code, transitions shipment to `DELIVERED`, and triggers payment settlement.

---

## 5. Digital Storage Verification Endpoints

### 5.1 Register Warehouse Batch Deposit
- **Endpoint:** `POST /api/v1/storage/batches`
- **Access:** `cooperative_admin`, `farmer`

**Request Payload:**
```json
{
  "facility_id": "fac-nashik-01",
  "crop_name": "Wheat",
  "weight_tons": 25.0,
  "moisture_percentage": 11.8,
  "storage_unit_identifier": "SILO-4A"
}
```

**Response Payload:**
```json
{
  "batch_id": "bat-wh-9120",
  "block_index": 149,
  "previous_block_hash": "0000a94bf128dc90e6712ab8e42091fc...",
  "current_block_hash": "c314b99a6809ef412850cd3194a82b7f...",
  "tamper_evident_status": "CRYPTOGRAPHICALLY_VERIFIED",
  "timestamp": "2026-10-30T10:30:00Z"
}
```

---

## 6. Central AI Recommendations Endpoint

### 6.1 Unified Decision Guidance
- **Endpoint:** `GET /api/v1/recommendations/my-recommendations`
- **Access:** `farmer`
- **Returns:** Prioritized array of actionable steps with human-readable rationales and financial loss impact scores.

