from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class VerificationSignal(Base):
    """Represents transparent creator verification trust badges."""
    __tablename__ = "verification_signals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)  # tool_verified, commercial_ready, prompt_tested
    badge_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    # Relationships
    creator = relationship("CreatorProfile", back_populates="verification_signals")
