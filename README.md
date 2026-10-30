# AgriShield AI — Backend Platform

AgriShield AI is a modular, scalable, and secure backend platform designed to prevent agricultural post-harvest loss and deliver actionable decision support for farmers, buyers, transporters, and cooperative societies across rural India.

---

## 1. Core Modules

1. **AI Freshness Intelligence Engine:**
   - Evaluates biological deterioration risk (0–100) using crop-specific respiratory dynamics ($Q_{10}$ thermal acceleration), relative humidity vapor pressure deficits, storage exposure, and transport conditions.
   - Hybrid architecture combining a calibrated agronomic rule engine with a Scikit-learn Random Forest regression model ($R^2 = 0.98$).
2. **Smart Surplus Aggregation Engine:**
   - Enables smallholder farmers with sub-truckload surplus to discover nearby farmers via the Haversine formula and pool produce into bulk lots.
   - Enforces transaction-safe atomic row locking (`with_for_update`) to prevent double-allocation race conditions.
3. **Marketplace & Buyer Management:**
   - Buyer requirement posting, multi-attribute offer comparison, and strict asset-ownership authorization checks for offer acceptance.
4. **Transportation Coordination:**
   - Vehicle registration, route queries, automated rural distance and cost estimation in INR, and delivery lifecycle tracking with 6-digit confirmation OTPs.
5. **Digital Storage Verification:**
   - Tamper-evident grain warehousing records using SHA-256 cryptographic hash chaining.
   - Explicit separation between digital record authenticity, inspection completion, and physical grain quality metrics.
6. **Unified AI Recommendation Engine:**
   - Synthesizes real-time signals across all modules to generate prioritized, explainable guidance for farmers (`URGENT_SALE`, `SURPLUS_AGGREGATION`, `OFFER_COMPARISON`, `COOPERATIVE_STORAGE`, `STORAGE_INSPECTION`).

---

## 2. Technology Stack

- **Runtime:** Python 3.12+ (Tested on Python 3.13)
- **Framework:** FastAPI
- **Database:** PostgreSQL (with SQLite support for unit testing)
- **ORM:** SQLAlchemy 2.0 (Declarative Base, 24 normalized relational tables)
- **Migrations:** Alembic
- **Validation:** Pydantic v2 (ConfigDict, strict types)
- **Authentication:** JWT (HMAC-SHA256) with refresh-token rotation and Argon2id password hashing
- **Machine Learning:** Scikit-learn, NumPy, Pandas, Joblib
- **Task Scheduling:** APScheduler (automated expiration cleanup)
- **Testing:** Pytest & HTTPX (19/19 automated tests passing)
- **Server:** Uvicorn ASGI

---

## 3. Directory Layout

```text
AgriShield-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint & lifespan
│   │   │
│   │   ├── core/                       # Core configuration, security & DB setup
│   │   │   ├── config.py               # Pydantic Settings & environment variables
│   │   │   ├── database.py             # SQLAlchemy 2.0 engine & session maker
│   │   │   ├── security.py             # Argon2id hashing & JWT token rotation
│   │   │   ├── dependencies.py         # DB session, auth, RBAC & rate limiting
│   │   │   ├── permissions.py          # UserRole enums & permission checkers
│   │   │   └── exceptions.py           # Domain-specific custom exceptions
│   │   │
│   │   ├── models/                     # 24 normalized SQLAlchemy models
│   │   │   ├── user.py                 # Users, Profiles, RefreshTokens
│   │   │   ├── crop.py                 # Crops, Guidelines, FreshnessAssessments
│   │   │   ├── surplus.py              # SurplusListings, AggregationGroups/Members
│   │   │   ├── marketplace.py          # BuyerRequirements, BuyerOffers
│   │   │   ├── transport.py            # TransportRequests, Offers, Shipments
│   │   │   ├── storage.py              # StorageFacilities, Batches, Inspections
│   │   │   ├── recommendation.py       # Multi-criteria Recommendations
│   │   │   └── audit.py                # AuditLogs, In-app Notifications
│   │   │
│   │   ├── schemas/                    # Pydantic v2 validation schemas
│   │   ├── repositories/               # Data access layer & atomic locking
│   │   ├── services/                   # Business logic & AI engines
│   │   │   ├── freshness_engine/       # Biological degradation & ML predictor
│   │   │   ├── surplus_engine/         # Surplus inventory & spatial lookup
│   │   │   ├── aggregation_engine/     # Bulk pooling & double-allocation locks
│   │   │   ├── storage_verification/   # Cryptographic SHA-256 hash chaining
│   │   │   ├── recommendation_engine/  # Central multi-criteria decision engine
│   │   │   └── ...
│   │   ├── api/v1/                     # Modular API route controllers
│   │   └── utils/                      # Haversine distance, cost heuristics & logging
│   │
│   ├── migrations/                     # Alembic database migrations
│   ├── tests/                          # Automated Pytest suite (19 test cases)
│   ├── scripts/
│   │   └── seed_demo_data.py           # Realistic Maharashtra demonstration dataset
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── alembic.ini
│   └── .env.example
│
├── ml/                                 # Machine Learning training & evaluation
│   ├── models/freshness_model.joblib   # Trained Scikit-learn Random Forest model
│   ├── training/                       # Dataset synthesis & model training script
│   ├── evaluation/                     # Cross-validation & metrics script
│   └── datasets/                       # Simulated agricultural telemetry dataset
│
└── DEVELOPMENT_STATUS.md               # Engineering verification & status document
```

---

## 4. Quick Start & Setup

### 4.1 Prerequisites
- Python 3.12+ (or 3.13)
- PostgreSQL 14+ (or SQLite fallback)

### 4.2 Clone & Install Dependencies
```bash
cd backend
python -m venv venv

# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

pip install -r requirements.txt
```

### 4.3 Configure Environment Variables
Copy `.env.example` to `.env` and verify database connection parameters:
```bash
cp .env.example .env
```
Default connection string:
```env
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/agrishield"
```

### 4.4 Run Database Migrations
Apply Alembic migrations to generate all 24 normalized tables and indexes:
```bash
alembic upgrade head
```

### 4.5 Seed Demonstration Data
Seed realistic demonstration entities (Tomatoes, Onions, Wheat, Farmers, Buyers, Transporters, Cooperatives, Batches):
```bash
python scripts/seed_demo_data.py
```

### 4.6 Start the FastAPI Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- ReDoc Interactive Documentation: `http://localhost:8000/redoc`
- System Health Check: `http://localhost:8000/health`

---

## 5. Running Automated Tests

Run the complete test suite with Pytest:
```bash
pytest -v
```
All 19 tests will execute against an isolated test database in under 1 second.

---

## 6. Docker Deployment

To spin up both PostgreSQL and the AgriShield AI API in isolated Docker containers:
```bash
docker-compose up --build -d
```
The application will automatically wait for the database, execute migrations, seed demonstration data, and launch Uvicorn with 4 workers on port 8000.
