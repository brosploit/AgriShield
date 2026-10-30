#!/usr/bin/env python3
"""AgriShield AI - Root Unified Server Runner

Run the entire application (FastAPI backend + Interactive Frontend Dashboard)
directly from the project root without needing to change directories:

    python run.py
"""

import os
import sys
from pathlib import Path

# Resolve root and backend directories
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# Ensure backend and ml directories are on sys.path
for directory in [str(BACKEND_DIR), str(ROOT_DIR)]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

# Load environment variables from root .env, or fallback to backend/.env
from dotenv import load_dotenv

if (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env")
elif (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")

import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("ENVIRONMENT", "development").lower() == "development"

    print("\n" + "=" * 65)
    print(" [AgriShield AI] - Unified Platform Server")
    print("=" * 65)
    print(f" * Web Portal:         http://localhost:{port}/")
    print(f" * Web Dashboard:      http://localhost:{port}/app/")
    print(f" * Operations Hub:     http://localhost:{port}/app/dashboard.html")
    print(f" * Interactive API:    http://localhost:{port}/docs")
    print(f" * Health Check:       http://localhost:{port}/health")
    print("=" * 65 + "\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        app_dir=str(BACKEND_DIR),
    )

