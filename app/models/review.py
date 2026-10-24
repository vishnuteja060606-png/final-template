from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class CreatorReview(Base):
    """
    Company reviews and ratings for AI creators.
    Allows brands and companies to evaluate creators on past work,
    quality of generation, brief adherence, and prompt turnaround.
    """
    __tablename__ = "creator_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=5)  # 1 to 5 stars
    project_title: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    tools_used: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g., "Runway Gen-3 + Midjourney v6"
    is_verified_engagement: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    creator = relationship("CreatorProfile", back_populates="reviews_received")
    company = relationship("CompanyProfile", back_populates="reviews_given")
