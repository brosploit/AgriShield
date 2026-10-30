# AgriShield AI — Project Dependencies & Environment Guide

This document provides a detailed breakdown of all Python dependencies defined in the project's root [`requirements.txt`](../requirements.txt) and [`backend/requirements.txt`](../backend/requirements.txt).

---

## 1. Dependency Directory & Categorization

| Category | Package | Version Constraint | Subsystem / Purpose |
| :--- | :--- | :--- | :--- |
| **Web Gateway** | `fastapi` | `>=0.115.0, <1.0.0` | Core asynchronous Web framework, OpenAPI generator, routing. |
| **ASGI Server** | `uvicorn[standard]` | `>=0.30.0, <1.0.0` | Lightning-fast ASGI production server with uvloop and websockets. |
| **ASGI Toolkit** | `starlette` | `>=0.38.0, <1.0.0` | Underlying ASGI toolkit providing static file mounting and requests. |
| **Database ORM** | `sqlalchemy` | `>=2.0.30, <3.0.0` | Declarative 2.0 ORM, 24 relational tables, atomic `with_for_update` row locks. |
| **Migrations** | `alembic` | `>=1.13.0, <2.0.0` | Database schema migrations, version tracking, DDL generation. |
| **Database Driver** | `psycopg2-binary` | `>=2.9.9, <3.0.0` | High-performance C-optimized PostgreSQL database adapter. |
| **Data Validation** | `pydantic` | `>=2.8.0, <3.0.0` | Strict data validation, schema enforcement, JSON serialization. |
| **Email Validation**| `email-validator` | `>=2.0.0, <3.0.0` | Email string validation for Pydantic models. |
| **Configuration** | `pydantic-settings`| `>=2.4.0, <3.0.0` | Environment variables parsing and `.env` file management. |
| **Environment** | `python-dotenv` | `>=1.0.1, <2.0.0` | Parses key-value pairs from `.env` files into environment variables. |
| **Form Data** | `python-multipart` | `>=0.0.9, <1.0.0` | Streaming multipart/form-data parser for file uploads. |
| **Authentication** | `pyjwt` | `>=2.8.0, <3.0.0` | Cryptographic JWT signing (HS256) and claims verification. |
| **Password Hashing**| `argon2-cffi` | `>=23.1.0, <25.0.0`| Memory-hard, timing-attack resistant password hashing (Argon2id). |
| **Cryptography** | `cryptography` | `>=42.0.0, <45.0.0`| Low-level cryptographic primitives and secure random tokens. |
| **Task Scheduling** | `apscheduler` | `>=3.10.4, <4.0.0` | In-process background job scheduler for automated expiration cleanup. |
| **Machine Learning**| `scikit-learn` | `>=1.5.0, <2.0.0` | Random Forest regression modeling ($R^2 = 0.98$), cross-validation. |
| **Numerical Array** | `numpy` | `>=1.26.0, <3.0.0` | Array manipulation, vector operations, and mathematical matrices. |
| **DataFrames** | `pandas` | `>=2.2.0, <3.0.0` | Tabular dataset synthesis, CSV I/O, telemetry aggregation. |
| **Model Persistence**| `joblib` | `>=1.4.0, <2.0.0` | Fast NumPy-aware binary serialization of trained ML estimators. |
| **Scientific Math** | `scipy` | `>=1.13.0, <2.0.0` | Scientific computing, optimization, and statistical distributions. |
| **Test Framework** | `pytest` | `>=8.0.0, <9.0.0` | Modern test runner executing the 19 integration test suites. |
| **Async Testing** | `pytest-asyncio` | `>=0.23.6, <1.0.0`| Asyncio fixture support for testing asynchronous endpoints. |
| **Test Coverage** | `pytest-cov` | `>=5.0.0, <6.0.0` | Line and branch coverage reporting (LCOV, HTML, terminal). |
| **HTTP Client** | `httpx` | `>=0.27.0, <1.0.0`| Asynchronous HTTP client for FastAPI TestClient and outbound APIs. |
| **Doc Site Builder**| `mkdocs` | `>=1.6.0, <2.0.0` | Static site generator designed for project documentation. |
| **Doc Theme** | `mkdocs-material` | `>=9.5.0, <10.0.0`| Material Design theme for MkDocs with search and code highlighting. |

---

## 2. Installation Profiles

### Profile A: Full Platform Installation (Recommended)
Installs all backend, machine learning, testing, and documentation packages:
```bash
# From repository root
pip install -r requirements.txt
```

### Profile B: Backend Only (Minimal Microservice)
Installs only the API gateway and database requirements:
```bash
cd backend
pip install -r requirements.txt
```

### Profile C: Documentation Generation
Installs documentation build tooling:
```bash
pip install mkdocs mkdocs-material pymdown-extensions
```

---

## 3. Verifying Installed Environment

Verify that the core dependencies are properly detected and functioning:

```bash
python -c "
import fastapi, sqlalchemy, pydantic, sklearn, numpy, pandas, joblib, argon2, jwt, apscheduler
print('FastAPI version:', fastapi.__version__)
print('SQLAlchemy version:', sqlalchemy.__version__)
print('Pydantic version:', pydantic.__version__)
print('Scikit-learn version:', sklearn.__version__)
print('All core dependencies imported successfully!')
"
```

---

## 4. Building the Documentation Site (Optional)

With `mkdocs-material` installed, you can launch a local documentation web server with instant live reloading:
```bash
# From repository root
mkdocs serve
```
Open `http://localhost:8000` (or `http://localhost:8001` if port 8000 is occupied by FastAPI) to explore the full interactive documentation.

To generate a static HTML distribution ready for GitHub Pages or static hosting:
```bash
mkdocs build
```
The static site will be compiled into `site/`.

