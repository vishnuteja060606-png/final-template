from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def get_utc_now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    """Base model for all SQLAlchemy entities."""
    pass
