"""AgriShield AI - Realistic Demonstration Data Seed Script

Seeds realistic agricultural demonstration entities across Maharashtra (Pune/Nashik rural corridor):
- Demonstration Crops (Tomatoes, Onions, Wheat, Rice, Soybean, Bananas)
- Demonstration Farmers, Buyers, Transporters, Cooperative Admins
- Active Surplus Listings & Aggregation Groups
- Storage Facilities & Cryptographically Verified Grain Batches
- Buyer Requirements & Active Offers
- Multi-criteria Unified Recommendations

All seeded data is explicitly labeled as demonstration data.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.permissions import UserRole
from app.core.security import compute_sha256, hash_password
from app.models.crop import Crop, CropGuideline, FreshnessAssessment
from app.models.marketplace import BuyerOffer, BuyerRequirement
from app.models.recommendation import Recommendation
from app.models.storage import StorageBatch, StorageFacility, StorageInspection, VerificationRecord
from app.models.surplus import AggregationGroup, AggregationMember, SurplusListing
from app.models.transport import Shipment, TransportOffer, TransportRequest
from app.models.user import (
    BuyerProfile,
    CooperativeProfile,
    FarmerProfile,
    TransporterProfile,
    User,
)
from app.utils.geo import estimate_transport_cost_inr, haversine_distance_km


def seed_database():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_admin = db.query(User).filter(User.email == "admin@agrishield.internal").first()
        if existing_admin:
            print("Database already contains demo seed data. Skipping seed.")
            return

        print("Seeding demonstration crops...")
        crops = {
            "tomato": Crop(
                name="Tomato",
                hindi_name="Tamatar",
                marathi_name="Tomato",
                category="perishable_vegetable",
                standard_shelf_life_days=10.0,
                optimal_temp_min_c=13.0,
                optimal_temp_max_c=18.0,
                optimal_humidity_min_pct=85.0,
                optimal_humidity_max_pct=95.0,
                respiration_rate="high",
                ethylene_sensitivity="high",
            ),
            "onion": Crop(
                name="Onion",
                hindi_name="Pyaaz",
                marathi_name="Kanda",
                category="perishable_vegetable",
                standard_shelf_life_days=120.0,
                optimal_temp_min_c=0.0,
                optimal_temp_max_c=25.0,
                optimal_humidity_min_pct=65.0,
                optimal_humidity_max_pct=75.0,
                respiration_rate="low",
                ethylene_sensitivity="low",
            ),
            "wheat": Crop(
                name="Wheat",
                hindi_name="Gehu",
                marathi_name="Gahu",
                category="durable_grain",
                standard_shelf_life_days=365.0,
                optimal_temp_min_c=10.0,
                optimal_temp_max_c=24.0,
                optimal_humidity_min_pct=50.0,
                optimal_humidity_max_pct=65.0,
                respiration_rate="very_low",
                ethylene_sensitivity="none",
            ),
            "rice": Crop(
                name="Rice",
                hindi_name="Chawal",
                marathi_name="Tandul",
                category="durable_grain",
                standard_shelf_life_days=365.0,
                optimal_temp_min_c=12.0,
                optimal_temp_max_c=25.0,
                optimal_humidity_min_pct=55.0,
                optimal_humidity_max_pct=70.0,
                respiration_rate="very_low",
                ethylene_sensitivity="none",
            ),
        }
        db.add_all(list(crops.values()))
        db.flush()

        print("Seeding crop guidelines...")
        guidelines = [
            CropGuideline(
                crop_id=crops["tomato"].id,
                storage_type="cold_storage",
                critical_temp_threshold_c=10.0,
                critical_humidity_threshold_pct=85.0,
                max_safe_storage_days=21.0,
                recommended_handling="Handle in plastic crates. Avoid stack pressure. Pre-cool within 4 hours of harvest.",
                post_harvest_care_tips="Maintain 13-15°C to avoid chilling injury while suppressing fungal pathogens.",
            ),
            CropGuideline(
                crop_id=crops["onion"].id,
                storage_type="ventilated_godown",
                critical_temp_threshold_c=30.0,
                critical_humidity_threshold_pct=70.0,
                max_safe_storage_days=90.0,
                recommended_handling="Cure outer skins in shade for 7-10 days before bulking in ventilated racks.",
                post_harvest_care_tips="Keep well-aerated with air circulation underneath bamboo rafters.",
            ),
            CropGuideline(
                crop_id=crops["wheat"].id,
                storage_type="grain_silo",
                critical_temp_threshold_c=28.0,
                critical_humidity_threshold_pct=65.0,
                max_safe_storage_days=365.0,
                recommended_handling="Ensure moisture level is below 12.0% before bagging or silo loading.",
                post_harvest_care_tips="Inspect monthly for sitophilus oryzae (weevils) and maintain phosphine gas seals if hermetic.",
            ),
        ]
        db.add_all(guidelines)
        db.flush()

        print("Seeding demonstration user accounts (Password: DemoPass123!)...")
        demo_pwd_hash = hash_password("DemoPass123!")

        # 1. Platform Admin
        admin_user = User(
            email="admin@agrishield.internal",
            phone_number="+919000000001",
            hashed_password=demo_pwd_hash,
            full_name="[DEMO] System Administrator",
            role=UserRole.PLATFORM_ADMIN.value,
            is_active=True,
            is_verified=True,
        )

        # 2. Farmers
        farmer1 = User(
            email="ramesh.patil@agrishield.demo",
            phone_number="+919822011111",
            hashed_password=demo_pwd_hash,
            full_name="[DEMO] Ramesh Bhaurao Patil",
            role=UserRole.FARMER.value,
            is_active=True,
            is_verified=True,
        )
        farmer2 = User(
            email="santosh.shinde@agrishield.demo",
            phone_number="+919822022222",
            hashed_password=demo_pwd_hash,
            full_name="[DEMO] Santosh Tukaram Shinde",
            role=UserRole.FARMER.value,
            is_active=True,
            is_verified=True,
        )

        # 3. Buyer
        buyer1 = User(
            email="vikram.shah@mumbaiagro.demo",
            phone_number="+919822033333",
            hashed_password=demo_pwd_hash,
            full_name="[DEMO] Vikram Shah (Vashi Wholesale Hub)",
            role=UserRole.BUYER.value,
            is_active=True,
            is_verified=True,
        )

        # 4. Transporter
        transporter1 = User(
            email="mahavir.logistics@agrishield.demo",
            phone_number="+919822044444",
            hashed_password=demo_pwd_hash,
            full_name="[DEMO] Mahavir Rural Roadways",
            role=UserRole.TRANSPORTER.value,
            is_active=True,
            is_verified=True,
        )

        # 5. Cooperative Admin
        coop_admin1 = User(
            email="junnar.sahakari@agrishield.demo",
            phone_number="+919822055555",
            hashed_password=demo_pwd_hash,
            full_name="[DEMO] Junnar Taluka Sahakari Kharedi Vikri Sangh",
            role=UserRole.COOPERATIVE_ADMIN.value,
            is_active=True,
            is_verified=True,
        )

        db.add_all([admin_user, farmer1, farmer2, buyer1, transporter1, coop_admin1])
        db.flush()

        # Profiles
        farmer1_profile = FarmerProfile(
            user_id=farmer1.id,
            village="Narayangaon",
            taluka_or_tehsil="Junnar",
            district="Pune",
            state="Maharashtra",
            pincode="410504",
            latitude=19.1245,
            longitude=73.9782,
            total_land_acres=4.5,
            primary_crops=["Tomato", "Onion"],
            preferred_language="mr",
        )
        farmer2_profile = FarmerProfile(
            user_id=farmer2.id,
            village="Alephata",
            taluka_or_tehsil="Junnar",
            district="Pune",
            state="Maharashtra",
            pincode="412411",
            latitude=19.1834,
            longitude=74.1032,
            total_land_acres=6.0,
            primary_crops=["Tomato", "Wheat"],
            preferred_language="mr",
        )
        buyer1_profile = BuyerProfile(
            user_id=buyer1.id,
            business_name="[DEMO] Sahyadri Fresh Processors Pvt Ltd",
            business_type="food_processor",
            gst_number="27AAACS1234F1Z5",
            city="Vashi, Navi Mumbai",
            district="Thane",
            state="Maharashtra",
            pincode="400703",
            delivery_address="Sector 19, APMC Vegetable Terminal, Vashi",
            latitude=19.0760,
            longitude=72.9982,
        )
        transporter1_profile = TransporterProfile(
            user_id=transporter1.id,
            vehicle_type="Tata 407 (Medium Duty)",
            vehicle_registration_number="MH-14-AZ-9988",
            capacity_tonnes=4.0,
            has_refrigeration=False,
            operating_radius_km=150.0,
            base_city="Narayangaon",
            base_latitude=19.1245,
            base_longitude=73.9782,
            rate_per_km_inr=28.0,
            is_available=True,
        )
        coop_profile = CooperativeProfile(
            user_id=coop_admin1.id,
            cooperative_name="[DEMO] Junnar Taluka Kisan Sahakari Sanstha",
            registration_number="COOP/PUNE/AGRI/2018/449",
            district="Pune",
            state="Maharashtra",
            total_member_farmers=850,
            contact_email="junnar.coop@agrishield.demo",
        )
        db.add_all([farmer1_profile, farmer2_profile, buyer1_profile, transporter1_profile, coop_profile])
        db.flush()

        print("Seeding storage facilities and batches...")
        facility = StorageFacility(
            cooperative_id=coop_admin1.id,
            facility_name="[DEMO] Narayangaon Modern Scientific Grain Silo",
            facility_type="grain_silo",
            village="Narayangaon",
            district="Pune",
            state="Maharashtra",
            total_capacity_mt=1200.0,
            available_capacity_mt=950.0,
            has_aeration=True,
            has_humidity_control=True,
            is_active=True,
        )
        db.add(facility)
        db.flush()

        # Create Verified Grain Batch
        now = datetime.now(timezone.utc)
        batch_id_str = "BATCH-202610-WHT-DEMO1"
        genesis_payload = {
            "batch_identifier": batch_id_str,
            "farmer_id": farmer2.id,
            "crop": "Wheat",
            "quantity": 5000.0,
            "salt": settings.STORAGE_HASH_SALT,
        }
        genesis_hash = compute_sha256(str(genesis_payload))

        batch = StorageBatch(
            batch_identifier=batch_id_str,
            farmer_id=farmer2.id,
            cooperative_id=coop_admin1.id,
            facility_id=facility.id,
            crop_id=crops["wheat"].id,
            quantity=5000.0,
            unit="kg",
            registration_timestamp=now - timedelta(days=5),
            current_hash=genesis_hash,
            verification_status="VERIFIED",
        )
        db.add(batch)
        db.flush()

        # Add Inspection & Verification Hash Chaining
        inspection_payload = {
            "batch_id": batch.id,
            "moisture_pct": 11.5,
            "temp_c": 21.0,
            "infestation": False,
        }
        insp_hash = compute_sha256(str(inspection_payload))
        chained_hash = compute_sha256(f"{genesis_hash}:{insp_hash}")
        batch.current_hash = chained_hash

        inspection = StorageInspection(
            batch_id=batch.id,
            inspector_id=coop_admin1.id,
            inspection_timestamp=now - timedelta(days=2),
            moisture_pct=11.5,
            temperature_c=21.0,
            humidity_pct=55.0,
            infestation_detected=False,
            foreign_matter_pct=0.2,
            physical_quality_score=96.0,
            physical_produce_quality_assessment="[DEMO] Premium Sharbati Wheat, uniform golden grain, safe moisture.",
            inspector_notes="Moisture meter calibrated. 10 core samples analyzed.",
            inspection_hash=insp_hash,
        )
        db.add(inspection)

        verif_record = VerificationRecord(
            batch_id=batch.id,
            previous_hash=genesis_hash,
            record_hash=chained_hash,
            record_authenticity_verified=True,
            inspection_completed=True,
            physical_quality_status="EXCELLENT",
            verified_by_id=coop_admin1.id,
            timestamp=now - timedelta(days=2),
            payload_snapshot=inspection_payload,
        )
        db.add(verif_record)

        print("Seeding surplus listings & freshness assessments...")
        # Freshness assessment for Farmer 1 Tomatoes
        fa1 = FreshnessAssessment(
            farmer_id=farmer1.id,
            crop_id=crops["tomato"].id,
            harvest_datetime=now - timedelta(hours=36),
            current_temperature_c=31.5,
            current_humidity_pct=52.0,
            storage_type="open_air",
            storage_duration_hours=36.0,
            transportation_conditions="ambient_open",
            crop_quantity_kg=1800.0,
            risk_score=68.5,
            risk_category="High",
            estimated_urgency="Urgent Action Required (24-48 Hours)",
            recommended_action="[DEMO] Fast-track sale to local puree unit or pool with nearby farmers for direct city dispatch.",
            influencing_factors_json={
                "temperature": "Ambient temperature of 31.5°C is well above 18°C optimal maximum.",
                "storage": "Open air storage accelerates moisture loss and fruit softening.",
            },
            model_version=settings.MODEL_VERSION,
            confidence_score=0.91,
        )
        db.add(fa1)
        db.flush()

        listing1 = SurplusListing(
            farmer_id=farmer1.id,
            crop_id=crops["tomato"].id,
            initial_quantity_kg=1800.0,
            available_quantity_kg=1800.0,
            quality_grade="Grade A",
            harvest_timestamp=now - timedelta(hours=36),
            expected_price_per_kg=24.0,
            currency="INR",
            village="Narayangaon",
            district="Pune",
            state="Maharashtra",
            latitude=19.1245,
            longitude=73.9782,
            freshness_assessment_id=fa1.id,
            status="active",
        )
        listing2 = SurplusListing(
            farmer_id=farmer2.id,
            crop_id=crops["tomato"].id,
            initial_quantity_kg=1200.0,
            available_quantity_kg=1200.0,
            quality_grade="Grade A",
            harvest_timestamp=now - timedelta(hours=24),
            expected_price_per_kg=24.0,
            currency="INR",
            village="Alephata",
            district="Pune",
            state="Maharashtra",
            latitude=19.1834,
            longitude=74.1032,
            status="active",
        )
        db.add_all([listing1, listing2])
        db.flush()

        print("Seeding buyer requirements & offers...")
        buyer_req = BuyerRequirement(
            buyer_id=buyer1.id,
            crop_id=crops["tomato"].id,
            required_quantity_kg=5000.0,
            fulfilled_quantity_kg=0.0,
            quality_grade_requirement="Grade A",
            target_price_per_kg=26.0,
            delivery_location="Vashi APMC Mandi, Navi Mumbai",
            delivery_district="Thane",
            delivery_latitude=19.0760,
            delivery_longitude=72.9982,
            delivery_deadline=now + timedelta(days=3),
            status="open",
        )
        db.add(buyer_req)
        db.flush()

        offer = BuyerOffer(
            buyer_id=buyer1.id,
            surplus_listing_id=listing1.id,
            buyer_requirement_id=buyer_req.id,
            offered_price_per_kg=25.5,
            offered_quantity_kg=1800.0,
            total_amount_inr=1800.0 * 25.5,
            terms="Immediate bank NEFT upon weighment at Vashi gate.",
            valid_until=now + timedelta(days=2),
            status="pending",
        )
        db.add(offer)

        print("Seeding multi-criteria recommendations...")
        rec1 = Recommendation(
            farmer_id=farmer1.id,
            related_crop_id=crops["tomato"].id,
            category="URGENT_SALE",
            priority="CRITICAL",
            explanation="High deterioration score (68.5%) on 1,800 kg Tomato lot due to 31.5°C open-air ambient storage.",
            supporting_information={"risk_score": 68.5, "temp_c": 31.5, "shelf_life_hours_remaining": 36},
            suggested_action="Review and accept pending buyer offer from Vikram Shah (INR 25.5/kg) before evening heat acceleration.",
        )
        rec2 = Recommendation(
            farmer_id=farmer2.id,
            related_crop_id=crops["wheat"].id,
            related_batch_id=batch.id,
            category="COOPERATIVE_STORAGE",
            priority="LOW",
            explanation="Batch 'BATCH-202610-WHT-DEMO1' successfully verified with 11.5% moisture and zero infestation.",
            supporting_information={"batch_identifier": batch_id_str, "status": "VERIFIED", "safe_storage_days": 270},
            suggested_action="Hold grain in Narayangaon silo until offseason price recovery in January 2027.",
        )
        db.add_all([rec1, rec2])

        db.commit()
        print("Demonstration data successfully seeded into AgriShield AI database!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
