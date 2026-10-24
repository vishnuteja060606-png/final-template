from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, get_utc_now

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="creator")  # creator, company, agency, admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Two-factor authentication (2FA) via email
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    email_otp_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # 1:1 Relationships
    creator_profile = relationship("CreatorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    company_profile = relationship("CompanyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def username(self) -> str:
        """Returns clean display username instead of email address."""
        if self.role == "creator" and self.creator_profile and self.creator_profile.display_name:
            return self.creator_profile.display_name
        if self.role in ["company", "agency"] and self.company_profile and self.company_profile.company_name:
            return self.company_profile.company_name
        if self.creator_profile and self.creator_profile.display_name:
            return self.creator_profile.display_name
        if self.company_profile and self.company_profile.company_name:
            return self.company_profile.company_name
        return self.email.split("@")[0]
