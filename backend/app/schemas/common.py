"""AgriShield AI - Common Pydantic Schemas

Defines generic response envelopes, pagination, and health checks.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str
    success: bool = True
    details: Optional[dict] = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    service: str = "AgriShield AI Backend"
    version: str
    environment: str
    database_connected: bool

