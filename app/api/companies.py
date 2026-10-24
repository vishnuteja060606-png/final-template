from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.company import (
    CompanyProfileCreate,
    CompanyProfileUpdate,
    CompanyProfileResponse,
    CompanyProfileCheckResponse
)
from app.services.company_service import company_service
from app.services.auth_service import get_current_user, get_current_user_optional, require_role

router = APIRouter(prefix="/api/companies", tags=["Companies"])

@router.get("", response_model=list[CompanyProfileResponse])
def list_companies(
    query: str | None = Query(None, description="Search companies by name or tag"),
    industry: str | None = Query(None, description="Filter by industry"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Rule: Companies should not see other companies
    if current_user and current_user.role in ["company", "agency"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Companies are not permitted to browse other companies."
        )
    return company_service.list_companies(db, query=query, industry=industry, limit=limit)

@router.get("/me", response_model=CompanyProfileResponse)
def get_my_company_profile(
    current_user: User = Depends(require_role(["company", "agency", "admin"])),
    db: Session = Depends(get_db)
):
    profile = company_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found for this account."
        )
    return profile

@router.get("/{company_id}", response_model=CompanyProfileResponse)
def get_company_by_id(
    company_id: int,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    # Rule: Companies should not see other companies
    if current_user and current_user.role in ["company", "agency"] and current_user.company_profile and current_user.company_profile.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Companies cannot view other company profiles."
        )

    profile = company_service.get_by_id(db, company_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found."
        )
    return profile

@router.post("/{company_id}/check", response_model=CompanyProfileCheckResponse)
def check_company_profile(
    company_id: int,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Check a company profile (specifically for creators).
    Persists check event in database and increments company view count.
    """
    company, view_record = company_service.record_company_profile_check(db, company_id, current_user)
    checked_by = None
    if current_user and current_user.role == "creator" and current_user.creator_profile:
        checked_by = current_user.creator_profile.display_name
    elif current_user:
        checked_by = current_user.username

    return CompanyProfileCheckResponse(
        message="Company profile checked and recorded in database.",
        company_id=company.id,
        company_name=company.company_name,
        views_count=company.views_count,
        checked_by_creator=checked_by,
        checked_at=view_record.checked_at
    )

@router.post("", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_company_profile(
    payload: CompanyProfileCreate,
    current_user: User = Depends(require_role(["company", "agency", "admin"])),
    db: Session = Depends(get_db)
):
    return company_service.create_profile(db, current_user.id, payload)

@router.put("/{company_id}", response_model=CompanyProfileResponse)
def update_company_profile(
    company_id: int,
    payload: CompanyProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = company_service.get_by_id(db, company_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found."
        )
    # Server-side ownership check
    if profile.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this company profile."
        )
    return company_service.update_profile(db, profile, payload)
