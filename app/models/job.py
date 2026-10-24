from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class Job(Base):
    """Represents a Creative Brief / Job Requirement posted by a Company."""
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    campaign_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)  # Video, Animation, Image, Graphic
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Cinematic, Hyper-real, Anime, Minimalist
    format: Mapped[str | None] = mapped_column(String(50), nullable=True)  # MP4, PNG, ProRes
    aspect_ratio: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)  # 16:9, 9:16, 1:1, 4:5
    commercial_use: Mapped[str | None] = mapped_column(String(100), default="Full Commercial Buyout")
    required_skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated
    required_tools: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated
    specialization: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    
    # Currency Fields (INR Primary, USD Calculated)
    budget_range: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "₹50,000 - ₹1,00,000"
    budget_inr: Mapped[int] = mapped_column(Integer, default=50000, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="published", index=True)  # draft, published, closed, archived
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    company = relationship("CompanyProfile", back_populates="jobs")
    engagements = relationship("Engagement", back_populates="job")

    @property
    def budget_usd(self) -> int:
        return round(self.budget_inr / 85.0)

    def skills_list(self) -> list[str]:
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(",") if s.strip()]

    def tools_list(self) -> list[str]:
        if not self.required_tools:
            return []
        return [t.strip() for t in self.required_tools.split(",") if t.strip()]
