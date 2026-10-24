from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.portfolio import PortfolioItem
from app.models.creator import CreatorProfile
from app.schemas.creator import CreatorProfileCreate, CreatorProfileUpdate, CreatorProfileResponse
from app.schemas.portfolio import PortfolioItemResponse, PortfolioPinToggleRequest
from app.services.creator_service import creator_service
from app.services.auth_service import get_current_user, get_current_user_optional, require_role

router = APIRouter(prefix="/api/creators", tags=["Creators"])

@router.get("", response_model=list[CreatorProfileResponse])
def list_creators_api(
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Rule: Creator should not able to see other creators
    if current_user and current_user.role == "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Creators are not permitted to browse other creators."
        )
    return db.query(CreatorProfile).filter(CreatorProfile.status == "published").all()

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
def get_creator_by_id(
    creator_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Rule: Creator should not able to see other creators
    if current_user and current_user.role == "creator" and current_user.creator_profile and current_user.creator_profile.id != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Creators cannot view other creator profiles."
        )

    profile = creator_service.get_by_id(db, creator_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator profile not found."
        )
    # Increment view count with session de-duplication
    session_key = (
        request.headers.get("x-session-id")
        or request.cookies.get("view_session")
        or request.cookies.get("session_id")
    )
    creator_service.increment_view(db, creator_id, session_key=session_key)
    db.refresh(profile)
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
    if profile:
        creator_id = profile.id
    elif current_user.role == "admin":
        item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio item not found.")
        creator_id = item.creator_id
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator profile not found.")
    
    return creator_service.toggle_pin_portfolio_item(db, creator_id, item_id, payload.is_pinned)

@router.post("/portfolio/{item_id}/view")
def increment_portfolio_item_view(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Increments view count for an individual portfolio item with session de-duplication.
    """
    session_key = (
        request.headers.get("x-session-id")
        or request.cookies.get("view_session")
        or request.cookies.get("session_id")
    )
    views = creator_service.increment_portfolio_view(db, item_id, session_key=session_key)
    return {"item_id": item_id, "views_count": views}
