from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class Engagement(Base):
    """
    Represents a Company engaging a Creator for a project or direct outreach.
    Includes comprehensive price bidding and two-way negotiation support.
    """
    __tablename__ = "engagements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)  # pending, accepted, declined, completed, negotiating
    message: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_budget: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Price Bidding & Negotiation
    bid_amount_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Initial price bid in INR
    counter_offer_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Counter-offer price bid in INR
    negotiation_status: Mapped[str | None] = mapped_column(String(50), default="initial_bid")  # initial_bid, counter_offered, agreed, declined
    negotiation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_negotiated_by: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 'company', 'creator'

    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    company = relationship("CompanyProfile", back_populates="engagements")
    creator = relationship("CreatorProfile", back_populates="engagements")
    job = relationship("Job", back_populates="engagements")

    @property
    def active_price_inr(self) -> int:
        """Returns currently active price bid (counter-offer if available, otherwise initial bid)."""
        if self.counter_offer_inr:
            return self.counter_offer_inr
        if self.bid_amount_inr:
            return self.bid_amount_inr
        # Try parse proposed_budget string if numerical
        if self.proposed_budget:
            clean = "".join(ch for ch in self.proposed_budget if ch.isdigit())
            if clean:
                return int(clean)
        return 0
