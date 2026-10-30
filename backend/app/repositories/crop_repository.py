"""AgriShield AI - Crop & Freshness Repository
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.crop import Crop, CropGuideline, FreshnessAssessment


class CropRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_crop_by_id(self, crop_id: str) -> Optional[Crop]:
        return self.db.query(Crop).filter(Crop.id == crop_id).first()

    def get_crop_by_name(self, name: str) -> Optional[Crop]:
        return self.db.query(Crop).filter(Crop.name.ilike(name.strip())).first()

    def get_all_crops(self) -> List[Crop]:
        return self.db.query(Crop).all()

    def create_crop(self, crop: Crop) -> Crop:
        self.db.add(crop)
        self.db.commit()
        self.db.refresh(crop)
        return crop

    def get_guidelines_for_crop(self, crop_id: str, storage_type: Optional[str] = None) -> List[CropGuideline]:
        query = self.db.query(CropGuideline).filter(CropGuideline.crop_id == crop_id)
        if storage_type:
            query = query.filter(CropGuideline.storage_type == storage_type)
        return query.all()

    def create_guideline(self, guideline: CropGuideline) -> CropGuideline:
        self.db.add(guideline)
        self.db.commit()
        self.db.refresh(guideline)
        return guideline

    def create_freshness_assessment(self, assessment: FreshnessAssessment) -> FreshnessAssessment:
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_assessment_by_id(self, assessment_id: str) -> Optional[FreshnessAssessment]:
        return self.db.query(FreshnessAssessment).filter(FreshnessAssessment.id == assessment_id).first()

    def get_farmer_assessments(self, farmer_id: str, limit: int = 50) -> List[FreshnessAssessment]:
        return (
            self.db.query(FreshnessAssessment)
            .filter(FreshnessAssessment.farmer_id == farmer_id)
            .order_by(FreshnessAssessment.assessment_timestamp.desc())
            .limit(limit)
            .all()
        )

