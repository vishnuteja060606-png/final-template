from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.portfolio import PortfolioItemResponse, PortfolioItemCreate, PortfolioItemUpdate
from app.services.portfolio_service import portfolio_service
from app.services.creator_service import creator_service
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/portfolio", tags=["Portfolios"])

@router.get("/{item_id}", response_model=PortfolioItemResponse)
def get_portfolio_item(item_id: int, db: Session = Depends(get_db)):
    item = portfolio_service.get_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found."
        )
    return item

@router.get("/creator/{creator_id}", response_model=list[PortfolioItemResponse])
def get_creator_portfolio(creator_id: int, db: Session = Depends(get_db)):
    return portfolio_service.list_by_creator(db, creator_id)

@router.post("", response_model=PortfolioItemResponse, status_code=status.HTTP_201_CREATED)
async def upload_portfolio_item(
    file: UploadFile = File(...),
    title: str = Form(...),
    content_type: str = Form(...),
    description: str | None = Form(None),
    aspect_ratio: str | None = Form(None),
    format: str | None = Form(None),
    tools_models: str | None = Form(None),
    skills: str | None = Form(None),
    specialization: str | None = Form(None),
    tags: str | None = Form(None),
    workflow: str | None = Form(None),
    current_user: User = Depends(require_role(["creator", "admin"])),
    db: Session = Depends(get_db)
):
    profile = creator_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set up your creator profile before uploading portfolio items."
        )

    metadata = PortfolioItemCreate(
        title=title,
        description=description,
        content_type=content_type,
        aspect_ratio=aspect_ratio,
        format=format,
        tools_models=tools_models,
        skills=skills,
        specialization=specialization,
        tags=tags,
        workflow=workflow
    )

    return await portfolio_service.create_item(db, profile.id, file, metadata)

@router.put("/{item_id}", response_model=PortfolioItemResponse)
def update_portfolio_item(
    item_id: int,
    payload: PortfolioItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = portfolio_service.get_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found."
        )
    # Server-side ownership check
    if item.creator.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this portfolio item."
        )
    return portfolio_service.update_item(db, item, payload)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = portfolio_service.get_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio item not found."
        )
    # Server-side ownership check
    if item.creator.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this portfolio item."
        )
    portfolio_service.delete_item(db, item)
    return None
