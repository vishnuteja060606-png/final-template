import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.review import CreatorReview
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.schemas.review import ReviewCreate, ReviewResponse, CreatorReviewsSummary

logger = logging.getLogger(__name__)

class ReviewService:
    def create_review(
        self, db: Session, company_user_id: int, creator_id: int, data: ReviewCreate
    ) -> CreatorReview:
        # Resolve company profile
        company = db.query(CompanyProfile).filter(CompanyProfile.user_id == company_user_id).first()
        if not company:
            # Fallback check if user_id was passed directly as company_id
            company = db.query(CompanyProfile).filter(CompanyProfile.id == company_user_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only registered companies can submit creator reviews."
            )

        creator = db.query(CreatorProfile).filter(CreatorProfile.id == creator_id).first()
        if not creator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Creator profile not found."
            )

        review = CreatorReview(
            creator_id=creator.id,
            company_id=company.id,
            rating=data.rating,
            project_title=data.project_title,
            comment=data.comment,
            tools_used=data.tools_used,
            is_verified_engagement=data.is_verified_engagement
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        logger.info(f"Created review {review.id} for creator {creator.id} by company {company.id}")
        return review

    def get_reviews_for_creator(self, db: Session, creator_id: int) -> CreatorReviewsSummary:
        creator = db.query(CreatorProfile).filter(CreatorProfile.id == creator_id).first()
        if not creator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

        reviews = db.query(CreatorReview).filter(CreatorReview.creator_id == creator_id).order_by(CreatorReview.created_at.desc()).all()
        
        review_items = []
        for r in reviews:
            comp_name = r.company.company_name if r.company else "Verified Client"
            comp_logo = r.company.logo_url if r.company else None
            review_items.append(
                ReviewResponse(
                    id=r.id,
                    creator_id=r.creator_id,
                    company_id=r.company_id,
                    company_name=comp_name,
                    company_logo=comp_logo,
                    rating=r.rating,
                    project_title=r.project_title,
                    comment=r.comment,
                    tools_used=r.tools_used,
                    is_verified_engagement=r.is_verified_engagement,
                    created_at=r.created_at
                )
            )

        avg_rating = creator.average_rating
        return CreatorReviewsSummary(
            creator_id=creator_id,
            average_rating=avg_rating,
            total_reviews=len(review_items),
            reviews=review_items
        )

review_service = ReviewService()
