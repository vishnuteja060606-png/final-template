from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.engagement import EngagementCreate, EngagementUpdate, EngagementResponse
from app.services.engagement_service import engagement_service
from app.services.company_service import company_service
from app.services.creator_service import creator_service
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/engagements", tags=["Engagements & Selection"])

@router.post("", response_model=EngagementResponse, status_code=status.HTTP_201_CREATED)
def create_engagement(
    payload: EngagementCreate,
    current_user: User = Depends(require_role(["company", "agency", "admin"])),
    db: Session = Depends(get_db)
):
    company = company_service.get_by_user_id(db, current_user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile must be set up before initiating engagements."
        )
    engagement = engagement_service.create_engagement(db, company.id, payload)
    return EngagementResponse(
        id=engagement.id,
        company_id=engagement.company_id,
        creator_id=engagement.creator_id,
        job_id=engagement.job_id,
        status=engagement.status,
        message=engagement.message,
        proposed_budget=engagement.proposed_budget,
        created_at=engagement.created_at,
        updated_at=engagement.updated_at,
        company_name=company.company_name,
        creator_name=engagement.creator.display_name if engagement.creator else None,
        job_title=engagement.job.title if engagement.job else None
    )

@router.get("/my", response_model=list[EngagementResponse])
def get_my_engagements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "creator":
        creator = creator_service.get_by_user_id(db, current_user.id)
        if not creator:
            return []
        engagements = engagement_service.list_for_creator(db, creator.id)
    else:
        company = company_service.get_by_user_id(db, current_user.id)
        if not company:
            return []
        engagements = engagement_service.list_for_company(db, company.id)

    return [
        EngagementResponse(
            id=e.id,
            company_id=e.company_id,
            creator_id=e.creator_id,
            job_id=e.job_id,
            status=e.status,
            message=e.message,
            proposed_budget=e.proposed_budget,
            created_at=e.created_at,
            updated_at=e.updated_at,
            company_name=e.company.company_name if e.company else None,
            creator_name=e.creator.display_name if e.creator else None,
            job_title=e.job.title if e.job else None
        )
        for e in engagements
    ]

@router.put("/{engagement_id}/status", response_model=EngagementResponse)
def update_engagement_status(
    engagement_id: int,
    payload: EngagementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    engagement = engagement_service.get_by_id(db, engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found."
        )

    # Permission check: Creator can accept/decline; Company can cancel/complete
    is_creator_owner = engagement.creator.user_id == current_user.id
    is_company_owner = engagement.company.user_id == current_user.id

    if not is_creator_owner and not is_company_owner and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this engagement."
        )

    updated = engagement_service.update_status(db, engagement, payload.status)
    return EngagementResponse(
        id=updated.id,
        company_id=updated.company_id,
        creator_id=updated.creator_id,
        job_id=updated.job_id,
        status=updated.status,
        message=updated.message,
        proposed_budget=updated.proposed_budget,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        company_name=updated.company.company_name if updated.company else None,
        creator_name=updated.creator.display_name if updated.creator else None,
        job_title=updated.job.title if updated.job else None
    )
