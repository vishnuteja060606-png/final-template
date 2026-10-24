from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class CompanyProfileView(Base):
    """
    Records when a creator (or user) checks a company's profile.
    Reflected and persisted in the database.
    """
    __tablename__ = "company_profile_views"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    viewer_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    creator_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    viewer_role: Mapped[str] = mapped_column(String(50), default="creator")
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, index=True)

    # Relationships
    company = relationship("CompanyProfile", back_populates="profile_views")
    creator = relationship("CreatorProfile", back_populates="company_views")
    viewer_user = relationship("User")
