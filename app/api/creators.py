from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.creator import CreatorProfileCreate, CreatorProfileUpdate, CreatorProfileResponse
from app.schemas.portfolio import PortfolioItemResponse, PortfolioPinToggleRequest
from app.services.creator_service import creator_service
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/creators", tags=["Creators"])

@router.get("/me", response_model=CreatorProfileResponse)
def get_my_creator_profile(
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    profile = creator_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator profile not found for this account."
        )
    return profile

@router.get("/{creator_id}", response_model=CreatorProfileResponse)
def get_creator_by_id(creator_id: int, db: Session = Depends(get_db)):
    profile = creator_service.get_by_id(db, creator_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator profile not found."
        )
    # Increment view count
    creator_service.increment_view(db, creator_id)
    return profile

@router.post("", response_model=CreatorProfileResponse, status_code=status.HTTP_201_CREATED)
def create_creator_profile(
    payload: CreatorProfileCreate,
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    return creator_service.create_profile(db, current_user.id, payload)

@router.put("/{creator_id}", response_model=CreatorProfileResponse)
def update_creator_profile(
    creator_id: int,
    payload: CreatorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = creator_service.get_by_id(db, creator_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator profile not found."
        )
    if profile.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this profile."
        )
    return creator_service.update_profile(db, profile, payload)

@router.post("/portfolio/{item_id}/pin", response_model=PortfolioItemResponse)
def toggle_pin_portfolio_work(
    item_id: int,
    payload: PortfolioPinToggleRequest,
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Reviewer Feature: Creator can pin their best work (up to 3 items).
    """
    profile = creator_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator profile not found.")
    
    return creator_service.toggle_pin_portfolio_item(db, profile.id, item_id, payload.is_pinned)
