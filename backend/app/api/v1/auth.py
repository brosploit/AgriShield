"""AgriShield AI - Authentication & Authorization API Endpoints
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, RateLimiter
from app.core.exceptions import (
    AuthenticationFailedException,
    EntityAlreadyExistsException,
    InvalidTokenException,
    TokenRevokedException,
)
from app.core.permissions import UserRole
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import FarmerProfile, RefreshToken, User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    LogoutRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(max_requests=settings.AUTH_RATE_LIMIT_PER_MINUTE))],
)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)

    # Check for duplicate email
    if user_repo.get_by_email(request.email):
        raise EntityAlreadyExistsException("User", "email", request.email)

    # Check for duplicate phone
    if user_repo.get_by_phone(request.phone_number):
        raise EntityAlreadyExistsException("User", "phone_number", request.phone_number)

    # Hash password with Argon2id
    hashed = hash_password(request.password)

    user = User(
        email=request.email.lower(),
        phone_number=request.phone_number,
        hashed_password=hashed,
        full_name=request.full_name,
        role=request.role.value,
        is_active=True,
        is_verified=False,
    )
    saved_user = user_repo.create_user(user)

    # If role is farmer and location provided, initialize FarmerProfile
    if request.role == UserRole.FARMER and (request.village or request.district):
        profile = FarmerProfile(
            user_id=saved_user.id,
            village=request.village or "Unknown",
            taluka_or_tehsil=request.village or "Unknown",
            district=request.district or "Unknown",
            state=request.state or "Maharashtra",
            pincode=request.pincode or "411001",
            latitude=request.latitude,
            longitude=request.longitude,
        )
        user_repo.create_or_update_farmer_profile(profile)

    return saved_user


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(RateLimiter(max_requests=settings.AUTH_RATE_LIMIT_PER_MINUTE))],
)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_identifier(request.identifier)

    if not user or not verify_password(request.password, user.hashed_password):
        raise AuthenticationFailedException("Invalid credentials. Please verify your email/phone and password.")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact administrator.",
        )

    # Create Access & Refresh Tokens
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token_str, jti, expire_dt = create_refresh_token(subject=user.id)

    # Store refresh token record for revocation tracking
    rt_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token_str),
        jti=jti,
        expires_at=expire_dt,
        is_revoked=False,
    )
    user_repo.save_refresh_token(rt_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)

    try:
        payload = decode_token(request.refresh_token)
    except Exception:
        raise InvalidTokenException("Invalid refresh token.")

    if payload.get("type") != "refresh":
        raise InvalidTokenException("Invalid token type. Expected refresh token.")

    jti = payload.get("jti")
    user_id = payload.get("sub")

    # Check revocation status
    rt_record = user_repo.get_refresh_token(jti)
    if not rt_record or rt_record.is_revoked:
        raise TokenRevokedException("Refresh token is revoked or already used.")

    # Invalidate old refresh token (Token Rotation)
    user_repo.revoke_refresh_token(jti)

    user = user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise AuthenticationFailedException("User not found or inactive.")

    # Issue new token pair
    new_access_token = create_access_token(subject=user.id, role=user.role)
    new_refresh_token_str, new_jti, new_expire = create_refresh_token(subject=user.id)

    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token_str),
        jti=new_jti,
        expires_at=new_expire,
        is_revoked=False,
    )
    user_repo.save_refresh_token(new_rt)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token_str,
        token_type="bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    if request.refresh_token:
        try:
            payload = decode_token(request.refresh_token)
            jti = payload.get("jti")
            if jti:
                user_repo.revoke_refresh_token(jti)
        except Exception:
            pass
    else:
        # Revoke all active sessions for this user
        user_repo.revoke_all_user_tokens(current_user.id)

    return MessageResponse(message="Successfully logged out and revoked session.")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(request.email)
    # Always return a generic success message to prevent user enumeration
    if user:
        # Generate temporary reset token (valid for 15 minutes)
        reset_token = create_access_token(
            subject=user.id,
            role="password_reset",
            extra_claims={"purpose": "pwd_reset"},
        )
        # In a real email setup, dispatch email. For offline/rural architecture, log or store securely.
        return MessageResponse(
            message="If the email exists, a password reset token has been generated.",
            details={"dev_reset_token": reset_token} if settings.DEBUG else None,
        )

    return MessageResponse(message="If the email exists, a password reset token has been generated.")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(request.token)
        if payload.get("purpose") != "pwd_reset":
            raise InvalidTokenException("Invalid reset token.")
        user_id = payload.get("sub")
    except Exception:
        raise InvalidTokenException("Invalid or expired password reset token.")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise AuthenticationFailedException("User not found.")

    user.hashed_password = hash_password(request.new_password)
    user_repo.update_user(user)
    user_repo.revoke_all_user_tokens(user.id)

    return MessageResponse(message="Password reset successfully. You may now log in with your new password.")

