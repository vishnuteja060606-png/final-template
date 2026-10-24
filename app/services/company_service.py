from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from app.models.company import CompanyProfile
from app.models.company_view import CompanyProfileView
from app.models.user import User
from app.schemas.company import CompanyProfileCreate, CompanyProfileUpdate

class CompanyService:
    @staticmethod
    def get_by_id(db: Session, company_id: int) -> CompanyProfile | None:
        return db.query(CompanyProfile).filter(CompanyProfile.id == company_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> CompanyProfile | None:
        return db.query(CompanyProfile).filter(CompanyProfile.user_id == user_id).first()

    @staticmethod
    def create_profile(db: Session, user_id: int, data: CompanyProfileCreate) -> CompanyProfile:
        existing = CompanyService.get_by_user_id(db, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company profile already exists for this user."
            )
        profile = CompanyProfile(
            user_id=user_id,
            company_name=data.company_name,
            industry=data.industry,
            description=data.description,
            website=data.website,
            location=data.location,
            tags=data.tags,
            views_count=0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(db: Session, profile: CompanyProfile, data: CompanyProfileUpdate) -> CompanyProfile:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def record_company_profile_check(
        db: Session, company_id: int, viewer_user: User | None = None
    ) -> tuple[CompanyProfile, CompanyProfileView]:
        """
        Records a check on a company profile (specifically by a creator or visitor).
        Increments view count and persists the check record in the database.
        """
        company = CompanyService.get_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company profile not found."
            )

        company.views_count = (company.views_count or 0) + 1

        creator_id = None
        viewer_role = "guest"
        user_id = None

        if viewer_user:
            user_id = viewer_user.id
            viewer_role = viewer_user.role
            if viewer_user.role == "creator" and viewer_user.creator_profile:
                creator_id = viewer_user.creator_profile.id

        view_entry = CompanyProfileView(
            company_id=company.id,
            viewer_user_id=user_id,
            creator_id=creator_id,
            viewer_role=viewer_role
        )
        db.add(view_entry)
        db.commit()
        db.refresh(company)
        db.refresh(view_entry)
        return company, view_entry

    @staticmethod
    def list_companies(
        db: Session, query: str | None = None, industry: str | None = None, limit: int = 50
    ) -> list[CompanyProfile]:
        """List companies with optional keyword/industry filters for creators exploring brands."""
        q = db.query(CompanyProfile)
        if query and query.strip():
            clean = f"%{query.strip().lower()}%"
            q = q.filter(
                or_(
                    func.lower(CompanyProfile.company_name).like(clean),
                    func.lower(CompanyProfile.description).like(clean),
                    func.lower(CompanyProfile.tags).like(clean)
                )
            )
        if industry and industry.strip():
            q = q.filter(func.lower(CompanyProfile.industry).like(f"%{industry.strip().lower()}%"))

        return q.order_by(CompanyProfile.views_count.desc(), CompanyProfile.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_companies_checked_by_creator(db: Session, creator_id: int, limit: int = 10) -> list[CompanyProfile]:
        """Retrieves distinct companies that have been checked by a specific creator."""
        checked_ids = (
            db.query(CompanyProfileView.company_id)
            .filter(CompanyProfileView.creator_id == creator_id)
            .distinct()
            .limit(limit)
            .all()
        )
        ids = [item[0] for item in checked_ids]
        if not ids:
            return []
        return db.query(CompanyProfile).filter(CompanyProfile.id.in_(ids)).all()

    @staticmethod
    def get_recent_creator_checks_for_company(db: Session, company_id: int, limit: int = 10) -> list[CompanyProfileView]:
        """Retrieves recent checks made on this company profile by creators."""
        return (
            db.query(CompanyProfileView)
            .filter(CompanyProfileView.company_id == company_id, CompanyProfileView.creator_id.isnot(None))
            .order_by(CompanyProfileView.checked_at.desc())
            .limit(limit)
            .all()
        )

company_service = CompanyService()
