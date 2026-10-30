"""AgriShield AI - Recommendation Schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RecommendationResponse(BaseModel):
    id: str
    farmer_id: str
    related_crop_id: Optional[str] = None
    crop_name: Optional[str] = None
    related_batch_id: Optional[str] = None
    batch_identifier: Optional[str] = None
    category: str
    priority: str
    explanation: str
    supporting_information: Dict[str, Any]
    suggested_action: str
    is_dismissed: bool
    creation_timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerateRecommendationsRequest(BaseModel):
    farmer_id: Optional[str] = None  # If null, generates for current farmer
    include_all_crops: bool = True

