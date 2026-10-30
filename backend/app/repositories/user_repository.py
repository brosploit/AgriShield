"""AgriShield AI - User & Profile Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import (
    User,
    FarmerProfile,
    BuyerProfile,
    TransporterProfile,
    CooperativeProfile,
    RefreshToken,
)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone_number == phone).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter((User.email == identifier.lower()) | (User.phone_number == identifier))
            .first()
        )

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    # Farmer Profile
    def get_farmer_profile(self, user_id: str) -> Optional[FarmerProfile]:
        return self.db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()

    def create_or_update_farmer_profile(self, profile: FarmerProfile) -> FarmerProfile:
        self.db.merge(profile)
        self.db.commit()
        return profile

    # Buyer Profile
    def get_buyer_profile(self, user_id: str) -> Optional[BuyerProfile]:
        return self.db.query(BuyerProfile).filter(BuyerProfile.user_id == user_id).first()

    def create_or_update_buyer_profile(self, profile: BuyerProfile) -> BuyerProfile:
        self.db.merge(profile)
        self.db.commit()
        return profile

    # Transporter Profile
    def get_transporter_profile(self, user_id: str) -> Optional[TransporterProfile]:
        return self.db.query(TransporterProfile).filter(TransporterProfile.user_id == user_id).first()

    def create_or_update_transporter_profile(self, profile: TransporterProfile) -> TransporterProfile:
        self.db.merge(profile)
        self.db.commit()
        return profile

    def get_available_transporters(self) -> List[TransporterProfile]:
        return self.db.query(TransporterProfile).filter(TransporterProfile.is_available.is_(True)).all()

    # Cooperative Profile
    def get_cooperative_profile(self, user_id: str) -> Optional[CooperativeProfile]:
        return self.db.query(CooperativeProfile).filter(CooperativeProfile.user_id == user_id).first()

    def create_or_update_cooperative_profile(self, profile: CooperativeProfile) -> CooperativeProfile:
        self.db.merge(profile)
        self.db.commit()
        return profile

    # Refresh Token Management
    def save_refresh_token(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.commit()
        return token

    def get_refresh_token(self, jti: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()

    def revoke_refresh_token(self, jti: str):
        token = self.get_refresh_token(jti)
        if token:
            token.is_revoked = True
            self.db.commit()

    def revoke_all_user_tokens(self, user_id: str):
        self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update({"is_revoked": True})
        self.db.commit()

