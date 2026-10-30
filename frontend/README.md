# AgriShield AI — Frontend Web Application

This directory contains the user interface for **AgriShield AI**, designed according to the Stitch design specifications (`DESIGN.md`).

---

## 1. Architecture & Pages

- **`index.html` (Landing Page):**
  Platform hero, post-harvest loss crisis metrics, core AI engine introductions, and navigation to stakeholder hubs.
- **`dashboard.html` (Farmer Operations Hub):**
  Real-time crop inventory, active yield telemetry, **interactive AI Freshness Assessment modal** (calculating biological deterioration risk, $Q_{10}$ thermal acceleration, and remaining shelf-life), **Crop Registration modal**, live buyer offers, and AI harvest guidance.
- **`climate.html` (Climate Intelligence):**
  24-hour diurnal micro-climate curves (Temperature & Humidity), 14-day agro-meteorological forecast matrix, extreme heat/frost tickers, and root-zone soil moisture depth profiles.
- **`transport.html` (Transport Facilities & Fleet Management):**
  Verified transport providers (Refrigerated cold-chain, heavy haulers, mini-trucks), **Schedule Transport modal** with real-time Haversine road distance & INR cost heuristics, and delivery tracking.
- **`storage.html` (Warehouse Availability & Cryptographic Vaults):**
  Nashik Sector 4 cooperative hub capacity & occupancy monitors, live atmospheric telemetry, and **Batch Deposit modal** with SHA-256 cryptographic tamper-evident receipt generation.
- **`api.js`:**
  Central API client communicating with FastAPI backend (`/api/v1`), with automated fallback to client-side biological calculation models when working offline.
- **`design/`:**
  Raw original Stitch dashboard export, design tokens (`DESIGN.md`), and UI screenshots.

---

## 2. How to Run

### Option A: Served via FastAPI Backend (Recommended)
When you start the FastAPI backend server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The entire frontend is automatically served at:
👉 **`http://localhost:8000/app/`**
- Operations Hub: `http://localhost:8000/app/dashboard.html`
- Climate Intelligence: `http://localhost:8000/app/climate.html`
- Transport Facilities: `http://localhost:8000/app/transport.html`
- Warehouse Fleet: `http://localhost:8000/app/storage.html`

### Option B: Standalone / Live Server
You can open `index.html` directly in any web browser or use VS Code Live Server / `npx serve`:
```bash
npx serve frontend -p 3000
```
Open `http://localhost:3000`. The frontend will detect whether the FastAPI backend is running on `http://localhost:8000` and automatically show an `API Online` or `Demo Mode (Offline)` status pill.

