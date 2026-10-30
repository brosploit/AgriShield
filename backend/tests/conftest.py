"""AgriShield AI - Pytest Configuration & Test Fixtures
"""

import os
import sys
from pathlib import Path
from typing import Generator
import pytest

# Ensure environment is set to testing before any imports
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_agrishield.db"

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test, expire_on_commit=False)

from app.core.config import settings
settings.ENVIRONMENT = "testing"
settings.DATABASE_URL = "sqlite:///:memory:"

from app.core.database import Base, get_db
from app.core.permissions import UserRole
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.crop import Crop
from app.models.user import FarmerProfile, User


@pytest.fixture(scope="session", autouse=True)
def init_test_schema():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session() -> Generator:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> Generator:
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def seed_test_users_and_crops(db_session):
    # Ensure crops exist
    tomato = db_session.query(Crop).filter(Crop.name == "Tomato").first()
    if not tomato:
        tomato = Crop(
            name="Tomato",
            category="perishable_vegetable",
            standard_shelf_life_days=10.0,
            optimal_temp_min_c=13.0,
            optimal_temp_max_c=18.0,
            optimal_humidity_min_pct=85.0,
            optimal_humidity_max_pct=95.0,
        )
        db_session.add(tomato)

    wheat = db_session.query(Crop).filter(Crop.name == "Wheat").first()
    if not wheat:
        wheat = Crop(
            name="Wheat",
            category="durable_grain",
            standard_shelf_life_days=365.0,
            optimal_temp_min_c=10.0,
            optimal_temp_max_c=24.0,
            optimal_humidity_min_pct=50.0,
            optimal_humidity_max_pct=65.0,
        )
        db_session.add(wheat)

    # Ensure users exist
    farmer = db_session.query(User).filter(User.email == "farmer.test@agrishield.internal").first()
    if not farmer:
        farmer = User(
            email="farmer.test@agrishield.internal",
            phone_number="+919876543210",
            hashed_password=hash_password("Password123!"),
            full_name="Ramesh Patil",
            role=UserRole.FARMER.value,
            is_active=True,
            is_verified=True,
        )
        db_session.add(farmer)
        db_session.flush()

        farmer_profile = FarmerProfile(
            user_id=farmer.id,
            village="Narayangaon",
            taluka_or_tehsil="Junnar",
            district="Pune",
            state="Maharashtra",
            pincode="410504",
            latitude=19.1245,
            longitude=73.9782,
            total_land_acres=5.5,
        )
        db_session.add(farmer_profile)

    buyer = db_session.query(User).filter(User.email == "buyer.test@agrishield.internal").first()
    if not buyer:
        buyer = User(
            email="buyer.test@agrishield.internal",
            phone_number="+919876543211",
            hashed_password=hash_password("Password123!"),
            full_name="Pooja Agro Traders",
            role=UserRole.BUYER.value,
            is_active=True,
            is_verified=True,
        )
        db_session.add(buyer)

    transporter = db_session.query(User).filter(User.email == "transporter.test@agrishield.internal").first()
    if not transporter:
        transporter = User(
            email="transporter.test@agrishield.internal",
            phone_number="+919876543212",
            hashed_password=hash_password("Password123!"),
            full_name="Kisan Logistics",
            role=UserRole.TRANSPORTER.value,
            is_active=True,
            is_verified=True,
        )
        db_session.add(transporter)

    coop_admin = db_session.query(User).filter(User.email == "coop.test@agrishield.internal").first()
    if not coop_admin:
        coop_admin = User(
            email="coop.test@agrishield.internal",
            phone_number="+919876543213",
            hashed_password=hash_password("Password123!"),
            full_name="Sahakari Godown Samiti",
            role=UserRole.COOPERATIVE_ADMIN.value,
            is_active=True,
            is_verified=True,
        )
        db_session.add(coop_admin)

    admin = db_session.query(User).filter(User.email == "admin.test@agrishield.internal").first()
    if not admin:
        admin = User(
            email="admin.test@agrishield.internal",
            phone_number="+919876543214",
            hashed_password=hash_password("Password123!"),
            full_name="Platform Admin",
            role=UserRole.PLATFORM_ADMIN.value,
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin)

    db_session.commit()

    return {
        "farmer": farmer,
        "buyer": buyer,
        "transporter": transporter,
        "coop_admin": coop_admin,
        "admin": admin,
        "crops": {"tomato": tomato, "wheat": wheat},
    }


@pytest.fixture
def farmer_token(seed_test_users_and_crops):
    user = seed_test_users_and_crops["farmer"]
    token = create_access_token(subject=user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def buyer_token(seed_test_users_and_crops):
    user = seed_test_users_and_crops["buyer"]
    token = create_access_token(subject=user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def transporter_token(seed_test_users_and_crops):
    user = seed_test_users_and_crops["transporter"]
    token = create_access_token(subject=user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def coop_token(seed_test_users_and_crops):
    user = seed_test_users_and_crops["coop_admin"]
    token = create_access_token(subject=user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token(seed_test_users_and_crops):
    user = seed_test_users_and_crops["admin"]
    token = create_access_token(subject=user.id, role=user.role)
    return {"Authorization": f"Bearer {token}"}
