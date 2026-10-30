# AgriShield AI — Deployment & Operations Guide

This guide covers local development setups, Docker container orchestration, database migrations, and production deployment considerations for AgriShield AI.

---

## 1. Local Development Setup

### 1.1 Prerequisites
- **Python:** 3.12 or 3.13
- **PostgreSQL:** 14+ (or SQLite fallback for testing)
- **Node.js:** v18+ (optional, only for standalone static serving)

### 1.2 Python Virtual Environment
```bash
cd backend
python -m venv venv

# Activate Virtual Environment:
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 1.3 Database Setup & Migrations
1. Create a PostgreSQL database named `agrishield`:
   ```sql
   CREATE DATABASE agrishield;
   ```
2. Copy environment settings:
   ```bash
   cp .env.example .env
   ```
3. Run Alembic schema migrations:
   ```bash
   alembic upgrade head
   ```
4. Seed realistic demonstration dataset:
   ```bash
   python scripts/seed_demo_data.py
   ```

### 1.4 Launch Unified Server
Start the Uvicorn ASGI server with automatic reload:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Access the application:
- **Web Dashboard:** `http://localhost:8000/app/`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Specifications:** `http://localhost:8000/redoc`
- **Health Check:** `http://localhost:8000/health`

---

## 2. Docker & Container Orchestration

A multi-container `docker-compose.yml` is provided to spin up PostgreSQL and the AgriShield AI API in isolated, pre-configured containers.

### 2.1 Launch Stack
```bash
cd backend
docker-compose up --build -d
```

### 2.2 Stack Services
- **`db` (PostgreSQL 15):** Exposes port `5433` on host, mapped to `5432` internally with persistent volume `postgres_data`.
- **`backend` (FastAPI App):** Builds via `Dockerfile`, waits for PostgreSQL to become healthy, executes migrations, seeds demonstration data, and launches Uvicorn on port `8000`.

### 2.3 Inspect Logs & Stop Stack
```bash
# View backend logs
docker-compose logs -f backend

# Stop stack
docker-compose down
```

---

## 3. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `"AgriShield AI"` | Application title across documentation and OpenAPI. |
| `ENVIRONMENT` | `"development"` | Mode (`development`, `testing`, `production`). |
| `DATABASE_URL` | `postgresql+psycopg2://...` | Connection URI for PostgreSQL or SQLite. |
| `SECRET_KEY` | `agrishield-dev-secret-key...` | Cryptographic secret for signing JWT access tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `60` | Duration before JWT access tokens expire. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duration before refresh tokens expire. |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000", ...]`| Whitelisted CORS origin URLs. |
| `ML_MODEL_PATH` | `"ml/models"` | Relative or absolute path to Scikit-learn `.joblib` model. |
| `STORAGE_HASH_SALT` | `"agrishield-grain-verification..."` | Cryptographic pepper for SHA-256 warehouse chaining. |

