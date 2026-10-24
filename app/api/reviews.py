from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, CreatorReviewsSummary
from app.services.review_service import review_service

router = APIRouter(prefix="/creators", tags=["Reviews"])

@router.post("/{creator_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_creator_review(
    creator_id: int,
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reviewer Feature: Company can give reviews and ratings for creators.
    """
    if current_user.role not in ["company", "agency", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only registered companies or agencies can submit creator reviews."
        )

    company_user_id = current_user.id
    review = review_service.create_review(db, company_user_id, creator_id, data)
    
    comp_name = review.company.company_name if review.company else current_user.username
    comp_logo = review.company.logo_url if review.company else None
    
    return ReviewResponse(
        id=review.id,
        creator_id=review.creator_id,
        company_id=review.company_id,
        company_name=comp_name,
        company_logo=comp_logo,
        rating=review.rating,
        project_title=review.project_title,
        comment=review.comment,
        tools_used=review.tools_used,
        is_verified_engagement=review.is_verified_engagement,
        created_at=review.created_at
    )

@router.get("/{creator_id}/reviews", response_model=CreatorReviewsSummary)
def list_creator_reviews(
    creator_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all company reviews and average rating for a creator.
    """
    return review_service.get_reviews_for_creator(db, creator_id)
