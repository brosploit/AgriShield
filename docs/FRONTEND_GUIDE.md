# AgriShield AI — Frontend Guide & Design System

The AgriShield AI frontend is an agricultural dashboard and web application built using the **Stitch Design System** (`frontend/design/agrishield_ai/DESIGN.md`), Tailwind CSS, Google Fonts, and Material Symbols.

---

## 1. Design Tokens & Palette

The visual design communicates agricultural vitality, trust, and technological clarity:

| Token Name | Hex Code | Role |
| :--- | :--- | :--- |
| `primary` | `#004c22` | Deep agricultural emerald for headers, primary CTAs, active sidebar pills. |
| `primary-container` | `#166534` | Forest green container for accented badges and cards. |
| `secondary` | `#006e2b` | Vibrant growth green for positive trends, optimum status badges. |
| `secondary-fixed` | `#6cff8a` | Electric mint for live sensor telemetry and pulsing status dots. |
| `surface` | `#f7faf3` | Clean neutral backdrop reflecting organic calmness. |
| `surface-container-low` | `#f1f5ed` | Soft card background for bento grids. |
| `surface-container-high`| `#e6e9e2` | Input fields, table row separators, and toggle controls. |
| `error` | `#ba1a1a` | Alert red for high deterioration risks, frost warnings, and critical alarms. |

### Typography
- **Headlines & Display:** `Plus Jakarta Sans` (SemiBold 600 & Bold 700)
- **Body & Labels:** `Inter` (Regular 400, Medium 500, SemiBold 600)
- **Icons:** `Material Symbols Outlined` via Google Fonts

---

## 2. Integrated Pages & Views

### 2.1 Landing Page (`index.html`)
- **Platform Hero:** Value propositions, real-time telemetry badge, and quick launch triggers.
- **Crisis Metrics Bento Grid:** Visual statistics on post-harvest spoilage ($14\text{--}22\%$), sub-truckload transport costs, and storage verification deficits.
- **Engine Feature Showcases:** Interactive deep-dive cards into AI Freshness, Surplus Aggregation, Transport Logistics, and Tamper-Proof Storage.

### 2.2 Operations Hub (`dashboard.html`)
- **Real-Time KPI Cards:** Active registered batches, surplus lots ready for aggregation, pending buyer offers, and deterioration warnings.
- **Active Crop Inventory Table:** Filterable inventory displaying batch IDs, quantities, storage conditions, and deterioration risk tags.
- **Interactive AI Freshness Modal:** Allows farmers to input crop type, current temperature, relative humidity, storage type, and duration. Calls the backend `/api/v1/freshness/assess` API and displays live risk scores, $Q_{10}$ acceleration factors, and recommendations.
- **Crop Registration Modal:** Instant crop batch intake form that dynamically updates the inventory.

### 2.3 Climate Intelligence (`climate.html`)
- **24-Hour Diurnal Curves:** Interactive SVG curve tracking temperature and relative humidity hourly trends.
- **14-Day Microclimate Matrix:** Daily day/night temperatures, rain probability, heat wave warnings, and optimal spray/harvest windows.
- **Soil Moisture Depth Profile:** Multilayer telemetry tracking topsoil ($0\text{--}15\text{ cm}$), root zone ($15\text{--}40\text{ cm}$), and deep vadose reserves.

### 2.4 Transport Facilities (`transport.html`)
- **Fleet Directory:** Verified transport providers filtered by vehicle type (Refrigerated cold-chain reefer trucks, heavy haulers, mini-trucks).
- **Haulage Quotation Modal:** Computes road distances using Haversine heuristics and generates instant INR (₹) estimates and dispatch OTP codes.
- **Live Dispatch Feed:** GPS route monitoring, delivery confirmation tokens, and continuous cold-chain temperature compliance logging.

### 2.5 Warehouse Fleet (`storage.html`)
- **Cooperative Hub Monitoring:** Real-time capacity and occupancy metrics across Nashik Central Hub, Niphad Cold Storage, and Pimpalgaon Silos.
- **Atmospheric Telemetry Modal:** Instant sensor breakdowns (temperature, RH, power backup status, CO2 purging).
- **Batch Deposit Modal:** Generates SHA-256 cryptographic tamper-evident receipts committed directly to the digital storage ledger.

---

## 3. Client-Side API Utility (`api.js`)

The `api.js` client connects the UI with the FastAPI backend while providing an autonomous offline fallback:
- **Health Polling:** Automatically verifies `http://localhost:8000/health` and toggles the header status badge (`● API Online` or `● Demo Mode`).
- **Offline Biochemical Simulator:** If the backend server is temporarily paused, `api.js` executes the exact mathematical formulas for $Q_{10}$ thermal degradation and vapor pressure deficit client-side, ensuring the UI remains 100% testable and interactive at all times.

