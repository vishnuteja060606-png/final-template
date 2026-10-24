import json
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    social_links: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: {linkedin, twitter, website}
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    user = relationship("User", back_populates="company_profile")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan", order_by="desc(Job.created_at)")
    engagements = relationship("Engagement", back_populates="company", cascade="all, delete-orphan")
    profile_views = relationship("CompanyProfileView", back_populates="company", cascade="all, delete-orphan", order_by="desc(CompanyProfileView.checked_at)")
    reviews_given = relationship("CreatorReview", back_populates="company", cascade="all, delete-orphan", order_by="desc(CreatorReview.created_at)")

    def social_links_dict(self) -> dict:
        if not self.social_links:
            return {}
        try:
            return json.loads(self.social_links)
        except Exception:
            return {}

    @property
    def total_jobs_posted(self) -> int:
        return len(self.jobs) if self.jobs else 0

    @property
    def total_reviews_given(self) -> int:
        return len(self.reviews_given) if self.reviews_given else 0
