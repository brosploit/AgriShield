"""AgriShield AI - API V1 Router Registry
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.farmers import router as farmers_router
from app.api.v1.buyers import router as buyers_router
from app.api.v1.transporters import router as transporters_router
from app.api.v1.freshness import router as freshness_router
from app.api.v1.surplus import router as surplus_router
from app.api.v1.aggregation import router as aggregation_router
from app.api.v1.storage import router as storage_router
from app.api.v1.cooperatives import router as cooperatives_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(farmers_router)
api_router.include_router(buyers_router)
api_router.include_router(transporters_router)
api_router.include_router(freshness_router)
api_router.include_router(surplus_router)
api_router.include_router(aggregation_router)
api_router.include_router(storage_router)
api_router.include_router(cooperatives_router)
api_router.include_router(recommendations_router)
api_router.include_router(notifications_router)
api_router.include_router(admin_router)

