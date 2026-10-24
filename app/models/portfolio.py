from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Video, Animation, Image, Graphic, 3D, Audio
    aspect_ratio: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)  # 16:9, 9:16, 1:1, 4:5, 21:9
    format: Mapped[str | None] = mapped_column(String(50), nullable=True)  # MP4, PNG, JPG, GIF, WebM
    tools_models: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated
    specialization: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated
    workflow: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Reviewer Requested Features
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)  # Pin best work (max 3 per creator)
    pin_order: Mapped[int] = mapped_column(Integer, default=0)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    creator = relationship("CreatorProfile", back_populates="portfolio_items")

    def tools_list(self) -> list[str]:
        if not self.tools_models:
            return []
        return [t.strip() for t in self.tools_models.split(",") if t.strip()]

    def skills_list(self) -> list[str]:
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def tags_list(self) -> list[str]:
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]
