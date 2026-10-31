# 🚀 Deploying AgriShield AI on Render (render.com)

This step-by-step guide explains how to deploy **AgriShield AI** (FastAPI backend + Interactive Stitch Frontend) on **Render** using either:
- **Method 1: 1-Click Infrastructure Blueprint (`render.yaml`) — Recommended**
- **Method 2: Manual Web Service Setup via Render Dashboard**

---

## ⚡ Architecture on Render

When deployed to Render:
- **Single Unified Web Service:** Render runs `python run.py`, hosting both the REST API (`/api/v1`) and the static frontend web application (`/app/` and `/`).
- **Dynamic Port Binding:** The application automatically binds to Render's assigned `$PORT` (typically port `10000`).
- **Zero-Config Database:** Automatically normalizes Render's `postgres://` URLs to SQLAlchemy 2.0 `postgresql+psycopg2://`, or defaults gracefully to SQLite if no external database is configured.
- **Auto Health Checks:** Render monitors `GET /health` every few seconds to guarantee zero-downtime deploys.

---

## Method 1: One-Click Blueprint Deployment (Recommended)

AgriShield AI includes a pre-configured [`render.yaml`](../render.yaml) file at the repository root that automatically sets up:
1. The **AgriShield AI Web Service** (Free tier).
2. A managed **Render PostgreSQL Database** (`agrishield-db`, Free tier).
3. Automatic database connection string injection.

### Steps:
1. **Push your code to GitHub / GitLab:**
   Ensure your repository has all latest commits and is pushed to your remote repository.

2. **Open Render Dashboard:**
   Go to [https://dashboard.render.com](https://dashboard.render.com) and log in.

3. **Deploy Blueprint:**
   - Click the **"New +"** button in the top right.
   - Select **"Blueprint"**.
   - Connect your GitHub repository (`AgriHub`).
   - Render will detect `render.yaml` automatically.
   - Click **"Apply"**.

4. **Wait for Build & Deploy:**
   - Render will provision the PostgreSQL database first.
   - Render will build the web service (`pip install -r requirements.txt`).
   - Once deployment completes, your public URL will be ready:
     `https://agrishield-ai.onrender.com/`

---

## Method 2: Manual Setup via Render Web UI

If you prefer to configure the service manually through Render's dashboard:

### Step 1: Create a PostgreSQL Database (Optional but Recommended)
1. On your Render Dashboard, click **New +** -> **PostgreSQL**.
2. Set:
   - **Name:** `agrishield-postgres`
   - **Database:** `agrishield`
   - **User:** `agrishield_user`
   - **Region:** *Choose closest to your users (e.g. Oregon or Frankfurt)*
   - **Plan:** **Free**
3. Click **Create Database**.
4. Once created, copy the **Internal Database URL** (e.g. `postgres://postgres:password@dpg-.../agrishield`).

### Step 2: Create the Web Service
1. On your Render Dashboard, click **New +** -> **Web Service**.
2. Select your repository: `AgriHub`.
3. Configure the following fields:

| Field | Value |
| :--- | :--- |
| **Name** | `agrishield-ai` |
| **Language / Runtime** | `Python 3` |
| **Region** | *Same as database (e.g., Oregon)* |
| **Branch** | `main` |
| **Root Directory** | *(Leave blank — uses root)* |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `python run.py` |
| **Instance Type** | **Free** |

### Step 3: Configure Environment Variables
Under the **Environment Variables** section, add:

| Key | Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.12.8` | Recommended stable Python runtime |
| `ENVIRONMENT` | `production` | Enables production caching |
| `DEBUG` | `false` | Disables debug stack traces in public responses |
| `SECRET_KEY` | *(Generate a 32+ character random string)* | Cryptographic JWT signing |
| `DATABASE_URL` | *Paste Internal Database URL from Step 1* | Render PostgreSQL (or leave empty for SQLite) |
| `STORAGE_HASH_SALT` | `agrishield-grain-verification-salt-2026` | SHA-256 warehouse receipt salt |

*(Note: If you do not attach a PostgreSQL database, leave `DATABASE_URL` blank. The backend will automatically fall back to an internal SQLite database).*

4. Click **Create Web Service**.

---

## 🔍 Verification & Post-Deployment Checklist

Once the deploy logs show `Uvicorn running on http://0.0.0.0:10000`:

1. **Open the Web Portal:**
   Visit your Render URL: `https://<your-service-name>.onrender.com/`
   - It will automatically redirect to the frontend application at `/app/`.

2. **Check System Health:**
   Visit `https://<your-service-name>.onrender.com/health`
   Expected response:
   ```json
   {
     "status": "ok",
     "service": "AgriShield AI",
     "version": "1.0.0",
     "environment": "production",
     "database_connected": true
   }
   ```

3. **Check Interactive API Docs:**
   Visit `https://<your-service-name>.onrender.com/docs` to test all OpenAPI endpoints.

4. **Test Frontend Workflow:**
   - Click **"Register / Sign In"** on the landing page.
   - Register a new farmer account or use the 1-click Demo accounts (`farmer.test@agrishield.internal` / `Password123!`).
   - Go to **Operations Hub** -> **Register New Crop** to verify live $Q_{10}$ freshness calculation.
   - Go to **Transport Facilities** to verify Haversine quote calculation and OTP generation.
   - Go to **Warehouse Fleet** to verify SHA-256 block ledger receipts.

---

## 🛠️ Built-in Render Compatibility Features

AgriShield AI was engineered with built-in Render optimizations:

1. **Automatic `postgres://` Protocol Translation:**
   SQLAlchemy 2.0 requires `postgresql+psycopg2://`. Render supplies `postgres://`. The database connector automatically converts legacy protocols on startup.
2. **Relative Frontend API Routing:**
   `frontend/api.js` automatically uses relative routes (`/api/v1` and `/health`) when hosted over HTTP/HTTPS, preventing hardcoded `localhost:8000` errors.
3. **Dynamic CORS Whitelisting:**
   The backend automatically allows all incoming requests originating from `*.onrender.com` domains.
4. **Graceful Database Fallback:**
   If a managed PostgreSQL database is unreachable or omitted, the application automatically boots on SQLite to ensure zero-downtime availability.

