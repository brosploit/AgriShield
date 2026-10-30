"""AgriShield AI - Schemas Registry
"""

from app.schemas.common import MessageResponse, PaginatedResponse, HealthCheckResponse
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.schemas.user import (
    FarmerProfileCreate,
    FarmerProfileResponse,
    BuyerProfileCreate,
    BuyerProfileResponse,
    TransporterProfileCreate,
    TransporterProfileResponse,
    CooperativeProfileCreate,
    CooperativeProfileResponse,
    UserProfileUpdate,
)
from app.schemas.crop import (
    CropCreate,
    CropResponse,
    CropGuidelineCreate,
    CropGuidelineResponse,
    FreshnessAssessmentRequest,
    FreshnessAssessmentResponse,
)
from app.schemas.surplus import (
    SurplusListingCreate,
    SurplusListingResponse,
    NearbySurplusQuery,
    AggregationGroupCreate,
    AggregationGroupResponse,
    AggregationMemberResponse,
    JoinAggregationRequest,
)
from app.schemas.marketplace import (
    BuyerRequirementCreate,
    BuyerRequirementResponse,
    BuyerOfferCreate,
    BuyerOfferResponse,
    OfferStatusUpdate,
)
from app.schemas.transport import (
    TransportRequestCreate,
    TransportRequestResponse,
    TransportOfferCreate,
    TransportOfferResponse,
    ShipmentResponse,
    ShipmentStatusUpdate,
)
from app.schemas.storage import (
    StorageFacilityCreate,
    StorageFacilityResponse,
    StorageBatchCreate,
    StorageBatchResponse,
    StorageInspectionCreate,
    StorageInspectionResponse,
    VerificationRecordResponse,
    BatchVerificationSummary,
)
from app.schemas.recommendation import (
    RecommendationResponse,
    GenerateRecommendationsRequest,
)
from app.schemas.notification import NotificationResponse

