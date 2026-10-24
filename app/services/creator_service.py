import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.creator import CreatorProfile
from app.models.portfolio import PortfolioItem
from app.models.verification import VerificationSignal
from app.schemas.creator import CreatorProfileCreate, CreatorProfileUpdate

logger = logging.getLogger(__name__)

class CreatorService:
    # In-memory session tracking for de-duplicated view analytics
    _viewed_creators: dict[str, set[int]] = {}
    _viewed_portfolio_items: dict[str, set[int]] = {}

    @classmethod
    def clear_view_cache(cls):
        """Reset view caches (primarily used in testing)."""
        cls._viewed_creators.clear()
        cls._viewed_portfolio_items.clear()

    @staticmethod
    def get_by_id(db: Session, creator_id: int) -> CreatorProfile | None:
        return db.query(CreatorProfile).filter(CreatorProfile.id == creator_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> CreatorProfile | None:
        return db.query(CreatorProfile).filter(CreatorProfile.user_id == user_id).first()

    @staticmethod
    def create_profile(db: Session, user_id: int, data: CreatorProfileCreate) -> CreatorProfile:
        existing = CreatorService.get_by_user_id(db, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Creator profile already exists for this user."
            )
        profile = CreatorProfile(
            user_id=user_id,
            display_name=data.display_name,
            headline=data.headline,
            bio=data.bio,
            specialization=data.specialization,
            skills=data.skills,
            tools_models=data.tools_models,
            workflow=data.workflow,
            experience_level=data.experience_level,
            location=data.location,
            website=data.website,
            social_links=data.social_links,
            specifications=data.specifications,
            hourly_rate_inr=data.hourly_rate_inr or 1500,
            profile_image_url=data.profile_image_url,
            status="draft"  # Starts in draft until at least 2 uploads are completed
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(db: Session, profile: CreatorProfile, data: CreatorProfileUpdate) -> CreatorProfile:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        # Enforce mandatory 2 uploads publication status
        upload_count = db.query(PortfolioItem).filter(PortfolioItem.creator_id == profile.id).count()
        if upload_count >= 2:
            profile.status = "published"
        else:
            profile.status = "draft"

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def refresh_publication_status(db: Session, creator_id: int) -> str:
        """
        Enforces reviewer requirement: At least 2 uploads mandatory.
        Automatically transitions between 'draft' and 'published'.
        """
        profile = CreatorService.get_by_id(db, creator_id)
        if not profile:
            return "draft"
        
        upload_count = db.query(PortfolioItem).filter(PortfolioItem.creator_id == creator_id).count()
        if upload_count >= 2:
            profile.status = "published"
        else:
            profile.status = "draft"
        
        db.commit()
        db.refresh(profile)
        return profile.status

    @classmethod
    def increment_view(cls, db: Session, creator_id: int, session_key: str | None = None) -> int:
        """
        Increments views_count with session de-duplication to prevent refresh spam.
        """
        profile = db.query(CreatorProfile).filter(CreatorProfile.id == creator_id).first()
        if not profile:
            return 0

        if session_key:
            viewed = cls._viewed_creators.setdefault(session_key, set())
            if creator_id in viewed:
                return profile.views_count or 0
            viewed.add(creator_id)

        profile.views_count = (profile.views_count or 0) + 1
        db.commit()
        db.refresh(profile)
        return profile.views_count

    @classmethod
    def increment_portfolio_view(cls, db: Session, item_id: int, session_key: str | None = None) -> int:
        """
        Increments portfolio item views_count with session de-duplication.
        """
        item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
        if not item:
            return 0

        if session_key:
            viewed = cls._viewed_portfolio_items.setdefault(session_key, set())
            if item_id in viewed:
                return item.views_count or 0
            viewed.add(item_id)

        item.views_count = (item.views_count or 0) + 1
        db.commit()
        db.refresh(item)
        return item.views_count

    @staticmethod
    def toggle_pin_portfolio_item(
        db: Session, creator_id: int, item_id: int, is_pinned: bool
    ) -> PortfolioItem:
        """
        Enforces reviewer requirement: Creator can pin their best work (up to 3 items).
        """
        item = db.query(PortfolioItem).filter(PortfolioItem.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio item not found."
            )

        if item.creator_id != creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to pin portfolio items that do not belong to you."
            )

        if is_pinned:
            # Check how many are already pinned (excluding this item)
            current_pinned = db.query(PortfolioItem).filter(
                PortfolioItem.creator_id == creator_id,
                PortfolioItem.is_pinned == True,
                PortfolioItem.id != item_id
            ).count()
            if current_pinned >= 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You can pin a maximum of 3 featured portfolio items."
                )
            item.is_pinned = True
            if not item.pin_order:
                item.pin_order = current_pinned + 1
        else:
            item.is_pinned = False
            item.pin_order = 0

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def calculate_completeness(profile: CreatorProfile) -> int:
        fields = [
            bool(profile.display_name),
            bool(profile.headline),
            bool(profile.bio),
            bool(profile.specialization),
            bool(profile.skills),
            bool(profile.tools_models),
            bool(profile.workflow),
            bool(profile.location),
            len(profile.portfolio_items) >= 2,  # Mandatory 2 uploads requirement
        ]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)

    @staticmethod
    def add_verification_badge(
        db: Session, creator_id: int, signal_type: str, badge_name: str, description: str | None = None
    ) -> VerificationSignal:
        signal = VerificationSignal(
            creator_id=creator_id,
            signal_type=signal_type,
            badge_name=badge_name,
            description=description
        )
        db.add(signal)
        profile = CreatorService.get_by_id(db, creator_id)
        if profile:
            profile.is_verified = True
        db.commit()
        db.refresh(signal)
        return signal

    @staticmethod
    def list_featured(db: Session, limit: int = 6) -> list[CreatorProfile]:
        return db.query(CreatorProfile).filter(
            CreatorProfile.status == "published"
        ).order_by(
            CreatorProfile.is_verified.desc(),
            CreatorProfile.views_count.desc(),
            CreatorProfile.created_at.desc()
        ).limit(limit).all()

creator_service = CreatorService()
