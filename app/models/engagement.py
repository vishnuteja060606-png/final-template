from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class Engagement(Base):
    """Represents a Company selecting or engaging a Creator for a project or direct outreach."""
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, accepted, declined, completed
    message: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_budget: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    company = relationship("CompanyProfile", back_populates="engagements")
    creator = relationship("CreatorProfile", back_populates="engagements")
    job = relationship("Job", back_populates="engagements")
