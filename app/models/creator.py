import json
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated list
    tools_models: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated list
    workflow: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    social_links: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: {twitter, instagram, artstation, youtube, github, linkedin, website}
    specifications: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: {hardware, resolution, max_fps, lora_training, turnaround_days, aspect_ratios}
    hourly_rate_inr: Mapped[int] = mapped_column(Integer, default=1500)  # Primary currency in INR (₹)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Reviewer Requested Features
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)  # 'draft' (if < 2 uploads), 'published' (if >= 2)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    user = relationship("User", back_populates="creator_profile")
    portfolio_items = relationship(
        "PortfolioItem",
        back_populates="creator",
        cascade="all, delete-orphan",
        order_by="desc(PortfolioItem.is_pinned), asc(PortfolioItem.pin_order), desc(PortfolioItem.created_at)"
    )
    verification_signals = relationship("VerificationSignal", back_populates="creator", cascade="all, delete-orphan")
    engagements = relationship("Engagement", back_populates="creator", cascade="all, delete-orphan")
    company_views = relationship("CompanyProfileView", back_populates="creator", cascade="all, delete-orphan")
    reviews_received = relationship("CreatorReview", back_populates="creator", cascade="all, delete-orphan", order_by="desc(CreatorReview.created_at)")
    connections_sent = relationship(
        "CreatorConnection",
        foreign_keys="CreatorConnection.requester_id",
        back_populates="requester",
        cascade="all, delete-orphan",
        order_by="desc(CreatorConnection.created_at)"
    )
    connections_received = relationship(
        "CreatorConnection",
        foreign_keys="CreatorConnection.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
        order_by="desc(CreatorConnection.created_at)"
    )

    def skills_list(self) -> list[str]:
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def tools_list(self) -> list[str]:
        if not self.tools_models:
            return []
        return [t.strip() for t in self.tools_models.split(",") if t.strip()]

    def specifications_dict(self) -> dict:
        if not self.specifications:
            return {}
        if isinstance(self.specifications, dict):
            return self.specifications
        try:
            val = json.loads(self.specifications)
            return val if isinstance(val, dict) else {"raw": str(val)}
        except Exception:
            return {"raw": self.specifications}

    def social_links_dict(self) -> dict:
        if not self.social_links:
            return {}
        if isinstance(self.social_links, dict):
            return self.social_links
        try:
            val = json.loads(self.social_links)
            return val if isinstance(val, dict) else {}
        except Exception:
            return {}

    @property
    def average_rating(self) -> float:
        if not self.reviews_received:
            return 5.0 if self.is_verified else 0.0
        ratings = [r.rating for r in self.reviews_received if r.rating]
        return round(sum(ratings) / len(ratings), 1) if ratings else 0.0

    @property
    def review_count(self) -> int:
        return len(self.reviews_received) if self.reviews_received else 0

    @property
    def published_uploads_count(self) -> int:
        return len(self.portfolio_items) if self.portfolio_items else 0

    @property
    def is_eligible_to_publish(self) -> bool:
        """Mandatory 2 uploads rule."""
        return self.published_uploads_count >= 2

    @property
    def pinned_portfolio_items(self) -> list:
        """Featured best works (max 3 items), sorted by pin order."""
        pinned = [p for p in (self.portfolio_items or []) if getattr(p, "is_pinned", False)]
        return sorted(
            pinned,
            key=lambda p: (
                getattr(p, "pin_order", 0) if (getattr(p, "pin_order", 0) or 0) > 0 else 99,
                -(getattr(p, "id", 0) or 0)
            )
        )[:3]

    @property
    def accepted_connections_count(self) -> int:
        count = 0
        for c in (self.connections_sent or []):
            if c.status == "accepted":
                count += 1
        for c in (self.connections_received or []):
            if c.status == "accepted":
                count += 1
        return count

    @property
    def pending_incoming_connections(self) -> list:
        return [c for c in (self.connections_received or []) if c.status == "pending"]

    @property
    def pending_outgoing_connections(self) -> list:
        return [c for c in (self.connections_sent or []) if c.status == "pending"]

    @property
    def accepted_connections(self) -> list:
        sent = [c for c in (self.connections_sent or []) if c.status == "accepted"]
        rec = [c for c in (self.connections_received or []) if c.status == "accepted"]
        return sent + rec
