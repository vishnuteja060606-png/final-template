from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.engagement import Engagement
from app.models.creator import CreatorProfile
from app.schemas.engagement import EngagementCreate

class EngagementService:
    @staticmethod
    def get_by_id(db: Session, engagement_id: int) -> Engagement | None:
        return db.query(Engagement).filter(Engagement.id == engagement_id).first()

    @staticmethod
    def create_engagement(db: Session, company_id: int, data: EngagementCreate) -> Engagement:
        creator = db.query(CreatorProfile).filter(CreatorProfile.id == data.creator_id).first()
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target creator profile not found."
            )
        engagement = Engagement(
            company_id=company_id,
            creator_id=data.creator_id,
            job_id=data.job_id,
            message=data.message,
            proposed_budget=data.proposed_budget,
            status="pending"
        )
        db.add(engagement)
        db.commit()
        db.refresh(engagement)
        return engagement

    @staticmethod
    def list_for_creator(db: Session, creator_id: int) -> list[Engagement]:
        return db.query(Engagement).filter(
            Engagement.creator_id == creator_id
        ).order_by(Engagement.created_at.desc()).all()

    @staticmethod
    def list_for_company(db: Session, company_id: int) -> list[Engagement]:
        return db.query(Engagement).filter(
            Engagement.company_id == company_id
        ).order_by(Engagement.created_at.desc()).all()

    @staticmethod
    def update_status(db: Session, engagement: Engagement, new_status: str) -> Engagement:
        allowed = ["pending", "accepted", "declined", "completed"]
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid engagement status. Allowed: {', '.join(allowed)}"
            )
        engagement.status = new_status
        db.commit()
        db.refresh(engagement)
        return engagement

engagement_service = EngagementService()
