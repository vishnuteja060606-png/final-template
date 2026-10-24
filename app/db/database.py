from typing import Generator
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.db.base import Base

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Create all tables in the database and ensure schema migrations."""
    # Import all models so that Base.metadata knows about them
    from app.models import (  # noqa: F401
        user, creator, portfolio, company, job, engagement,
        verification, company_view, sidecar, review, connection
    )
    Base.metadata.create_all(bind=engine)

    # Safe auto-migration for existing SQLite database
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    with engine.connect() as conn:
        # 1. Check creator_profiles
        if "creator_profiles" in table_names:
            c_cols = [col["name"] for col in inspector.get_columns("creator_profiles")]
            if "status" not in c_cols:
                conn.execute(text("ALTER TABLE creator_profiles ADD COLUMN status VARCHAR(50) DEFAULT 'draft'"))
            if "views_count" not in c_cols:
                conn.execute(text("ALTER TABLE creator_profiles ADD COLUMN views_count INTEGER DEFAULT 0"))
            if "hourly_rate_inr" not in c_cols:
                conn.execute(text("ALTER TABLE creator_profiles ADD COLUMN hourly_rate_inr INTEGER DEFAULT 1500"))
            if "website" not in c_cols:
                conn.execute(text("ALTER TABLE creator_profiles ADD COLUMN website VARCHAR(255)"))
            if "social_links" not in c_cols:
                conn.execute(text("ALTER TABLE creator_profiles ADD COLUMN social_links TEXT"))
            if "specifications" not in c_cols:
                conn.execute(text("ALTER TABLE creator_profiles ADD COLUMN specifications TEXT"))

        # 2. Check company_profiles
        if "company_profiles" in table_names:
            comp_cols = [col["name"] for col in inspector.get_columns("company_profiles")]
            if "views_count" not in comp_cols:
                conn.execute(text("ALTER TABLE company_profiles ADD COLUMN views_count INTEGER DEFAULT 0"))
            if "logo_url" not in comp_cols:
                conn.execute(text("ALTER TABLE company_profiles ADD COLUMN logo_url VARCHAR(500)"))
            if "social_links" not in comp_cols:
                conn.execute(text("ALTER TABLE company_profiles ADD COLUMN social_links TEXT"))

        # 3. Check portfolio_items
        if "portfolio_items" in table_names:
            p_cols = [col["name"] for col in inspector.get_columns("portfolio_items")]
            if "is_pinned" not in p_cols:
                conn.execute(text("ALTER TABLE portfolio_items ADD COLUMN is_pinned BOOLEAN DEFAULT 0"))
            if "pin_order" not in p_cols:
                conn.execute(text("ALTER TABLE portfolio_items ADD COLUMN pin_order INTEGER DEFAULT 0"))
            if "views_count" not in p_cols:
                conn.execute(text("ALTER TABLE portfolio_items ADD COLUMN views_count INTEGER DEFAULT 0"))

        # 4. Check jobs
        if "jobs" in table_names:
            j_cols = [col["name"] for col in inspector.get_columns("jobs")]
            if "budget_inr" not in j_cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN budget_inr INTEGER DEFAULT 50000"))

        conn.commit()
