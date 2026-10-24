from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.engagement import EngagementCreate, EngagementUpdate, EngagementResponse, CounterOfferRequest
from app.services.engagement_service import engagement_service
from app.services.company_service import company_service
from app.services.creator_service import creator_service
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/engagements", tags=["Engagements & Selection"])

def _to_response(engagement) -> EngagementResponse:
    return EngagementResponse(
        id=engagement.id,
        company_id=engagement.company_id,
        creator_id=engagement.creator_id,
        job_id=engagement.job_id,
        status=engagement.status,
        message=engagement.message,
        proposed_budget=engagement.proposed_budget,
        bid_amount_inr=engagement.bid_amount_inr,
        counter_offer_inr=engagement.counter_offer_inr,
        negotiation_status=engagement.negotiation_status,
        negotiation_notes=engagement.negotiation_notes,
        last_negotiated_by=engagement.last_negotiated_by,
        active_price_inr=engagement.active_price_inr,
        created_at=engagement.created_at,
        updated_at=engagement.updated_at,
        company_name=engagement.company.company_name if engagement.company else None,
        creator_name=engagement.creator.display_name if engagement.creator else None,
        job_title=engagement.job.title if engagement.job else None
    )

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
    return _to_response(engagement)

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

    return [_to_response(e) for e in engagements]

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
    return _to_response(updated)

@router.post("/{engagement_id}/counter-offer", response_model=EngagementResponse)
def submit_counter_offer(
    engagement_id: int,
    payload: CounterOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Price Negotiation: Submit a negotiated price counter-offer with terms in INR.
    """
    updated = engagement_service.submit_counter_offer(db, engagement_id, current_user, payload)
    return _to_response(updated)

@router.post("/{engagement_id}/accept-bid", response_model=EngagementResponse)
def accept_negotiated_bid(
    engagement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept the current price bid / counter-offer and agree on engagement terms.
    """
    updated = engagement_service.accept_bid(db, engagement_id, current_user)
    return _to_response(updated)
