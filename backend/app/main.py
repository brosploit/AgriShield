"""AgriShield AI - Main FastAPI Application

Initializes application, CORS middleware, centralized exception handling,
lifespan startup/shutdown, database verification, and API routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from apscheduler.schedulers.background import BackgroundScheduler

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.exceptions import AgriShieldException
from app.schemas.common import HealthCheckResponse
from app.utils.logger import get_logger

logger = get_logger("agrishield.main")

# Background job scheduler for automated expiration cleanup
scheduler = BackgroundScheduler()


def run_stale_records_cleanup():
    """Periodic job to update expired aggregation groups and buyer offers."""
    try:
        from app.models.marketplace import BuyerOffer
        from app.models.surplus import AggregationGroup
        from datetime import datetime, timezone

        db = SessionLocal()
        now = datetime.now(timezone.utc)
        # Expire stale offers
        expired_offers = (
            db.query(BuyerOffer)
            .filter(BuyerOffer.valid_until < now, BuyerOffer.status == "pending")
            .update({"status": "expired"})
        )
        # Expire stale groups
        expired_groups = (
            db.query(AggregationGroup)
            .filter(AggregationGroup.expiry_timestamp < now, AggregationGroup.status == "forming")
            .update({"status": "cancelled"})
        )
        if expired_offers or expired_groups:
            db.commit()
            logger.info(f"Cleanup executed: {expired_offers} offers expired, {expired_groups} groups expired.")
        db.close()
    except Exception as e:
        logger.warning(f"Error in stale records cleanup job: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only run DB migration and background scheduler if not in testing mode
    if settings.ENVIRONMENT != "testing":
        try:
            logger.info("Initializing AgriShield database models...")
            Base.metadata.create_all(bind=engine)
            if not scheduler.running:
                scheduler.add_job(run_stale_records_cleanup, "interval", minutes=30, id="stale_cleanup")
                scheduler.start()
                logger.info("Background scheduler initialized.")
        except Exception as e:
            logger.warning(f"Startup warning: {e}")

    yield

    # Shutdown
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler terminated.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AI-powered agricultural post-harvest loss prevention and decision-support backend platform. "
        "Provides AI Freshness Intelligence, Smart Surplus Aggregation, Transportation Coordination, "
        "and Digital Grain Storage Verification."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Centralized Custom Exception Handler
@app.exception_handler(AgriShieldException)
async def agrishield_exception_handler(request: Request, exc: AgriShieldException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "success": False,
        },
    )


# Health Check Endpoints
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", response_model=HealthCheckResponse, tags=["Health"])
def health_check():
    db_connected = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_connected = True
    except Exception as err:
        logger.error(f"Database health check failed: {err}")

    return HealthCheckResponse(
        status="ok" if db_connected else "degraded",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database_connected=db_connected,
    )


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "active",
        "documentation": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
    }


# Mount API V1 Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

