from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class CreatorConnection(Base):
    """
    Mutual professional networking connections between AI Creators.
    Status transitions: 'pending' -> 'accepted' or 'rejected'.
    """
    __tablename__ = "creator_connections"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id: Mapped[int] = mapped_column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)  # 'pending', 'accepted', 'rejected'
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    requester = relationship("CreatorProfile", foreign_keys=[requester_id], back_populates="connections_sent")
    receiver = relationship("CreatorProfile", foreign_keys=[receiver_id], back_populates="connections_received")

    __table_args__ = (
        UniqueConstraint("requester_id", "receiver_id", name="uq_creator_connection_pair"),
    )

    def other_creator(self, current_creator_id: int):
        """Returns the other CreatorProfile in this connection pair."""
        if self.requester_id == current_creator_id:
            return self.receiver
        return self.requester
