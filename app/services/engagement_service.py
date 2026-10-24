from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.engagement import Engagement
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.models.user import User
from app.schemas.engagement import EngagementCreate, CounterOfferRequest

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
        
        # Calculate numerical bid in INR if not provided
        bid_inr = data.bid_amount_inr
        if not bid_inr and data.proposed_budget:
            digits = "".join(c for c in data.proposed_budget if c.isdigit())
            if digits:
                bid_inr = int(digits)

        engagement = Engagement(
            company_id=company_id,
            creator_id=data.creator_id,
            job_id=data.job_id,
            message=data.message,
            proposed_budget=data.proposed_budget,
            bid_amount_inr=bid_inr,
            negotiation_status="initial_bid",
            last_negotiated_by="company",
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
        allowed = ["pending", "accepted", "declined", "completed", "negotiating"]
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid engagement status. Allowed: {', '.join(allowed)}"
            )
        engagement.status = new_status
        if new_status == "accepted":
            engagement.negotiation_status = "agreed"
        elif new_status == "declined":
            engagement.negotiation_status = "declined"
        db.commit()
        db.refresh(engagement)
        return engagement

    @staticmethod
    def submit_counter_offer(
        db: Session,
        engagement_id: int,
        current_user: User,
        data: CounterOfferRequest
    ) -> Engagement:
        engagement = EngagementService.get_by_id(db, engagement_id)
        if not engagement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Engagement proposal not found.")

        # Check permission: user must be either the creator or the company
        is_creator = current_user.creator_profile and current_user.creator_profile.id == engagement.creator_id
        is_company = current_user.company_profile and current_user.company_profile.id == engagement.company_id

        if not is_creator and not is_company and current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to negotiate this engagement.")

        sender_role = "creator" if is_creator else "company"
        engagement.counter_offer_inr = data.counter_offer_inr
        engagement.negotiation_status = "counter_offered"
        engagement.negotiation_notes = data.notes
        engagement.last_negotiated_by = sender_role
        engagement.status = "pending"

        db.commit()
        db.refresh(engagement)
        return engagement

    @staticmethod
    def accept_bid(db: Session, engagement_id: int, current_user: User) -> Engagement:
        engagement = EngagementService.get_by_id(db, engagement_id)
        if not engagement:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Engagement proposal not found.")

        is_creator = current_user.creator_profile and current_user.creator_profile.id == engagement.creator_id
        is_company = current_user.company_profile and current_user.company_profile.id == engagement.company_id

        if not is_creator and not is_company and current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to accept this engagement.")

        engagement.status = "accepted"
        engagement.negotiation_status = "agreed"
        db.commit()
        db.refresh(engagement)
        return engagement

engagement_service = EngagementService()
