import logging
from typing import Generator
from sqlalchemy import create_engine, inspect, text, event
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

# Connection pooling & engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production-ready connection pooling for PostgreSQL / MySQL
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_timeout": 30,
    })

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# Enable foreign keys for SQLite connections
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def configure_sqlite_connection(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    """Verifies active connectivity to the underlying database."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

def init_db() -> None:
    """Create all tables in the database and ensure safe schema migrations."""
    # Import all models so that Base.metadata knows about them
    from app.models import (  # noqa: F401
        user, creator, portfolio, company, job, engagement,
        verification, company_view, sidecar, review, connection
    )
    Base.metadata.create_all(bind=engine)

    # Safe auto-migration for existing database schemas (SQLite / PostgreSQL)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    with engine.connect() as conn:
        def _safe_add_column(table: str, col_name: str, col_def: str, existing_cols: list[str]):
            if col_name not in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"))
                    logger.info(f"Auto-migrated: added column {col_name} to table {table}")
                except Exception as ex:
                    logger.warning(f"Notice during migration of {table}.{col_name}: {ex}")

        # 1. Check creator_profiles
        if "creator_profiles" in table_names:
            c_cols = [col["name"] for col in inspector.get_columns("creator_profiles")]
            _safe_add_column("creator_profiles", "status", "VARCHAR(50) DEFAULT 'draft'", c_cols)
            _safe_add_column("creator_profiles", "views_count", "INTEGER DEFAULT 0", c_cols)
            _safe_add_column("creator_profiles", "hourly_rate_inr", "INTEGER DEFAULT 1500", c_cols)
            _safe_add_column("creator_profiles", "website", "VARCHAR(255)", c_cols)
            _safe_add_column("creator_profiles", "social_links", "TEXT", c_cols)
            _safe_add_column("creator_profiles", "specifications", "TEXT", c_cols)
            _safe_add_column("creator_profiles", "is_verified", "BOOLEAN DEFAULT 0", c_cols)

        # 2. Check company_profiles
        if "company_profiles" in table_names:
            comp_cols = [col["name"] for col in inspector.get_columns("company_profiles")]
            _safe_add_column("company_profiles", "views_count", "INTEGER DEFAULT 0", comp_cols)
            _safe_add_column("company_profiles", "logo_url", "VARCHAR(500)", comp_cols)
            _safe_add_column("company_profiles", "social_links", "TEXT", comp_cols)
            _safe_add_column("company_profiles", "location", "VARCHAR(100)", comp_cols)
            _safe_add_column("company_profiles", "website", "VARCHAR(255)", comp_cols)
            _safe_add_column("company_profiles", "tags", "TEXT", comp_cols)

        # 3. Check portfolio_items
        if "portfolio_items" in table_names:
            p_cols = [col["name"] for col in inspector.get_columns("portfolio_items")]
            _safe_add_column("portfolio_items", "is_pinned", "BOOLEAN DEFAULT 0", p_cols)
            _safe_add_column("portfolio_items", "pin_order", "INTEGER DEFAULT 0", p_cols)
            _safe_add_column("portfolio_items", "views_count", "INTEGER DEFAULT 0", p_cols)
            _safe_add_column("portfolio_items", "tools_models", "TEXT", p_cols)
            _safe_add_column("portfolio_items", "skills", "TEXT", p_cols)
            _safe_add_column("portfolio_items", "specialization", "VARCHAR(100)", p_cols)
            _safe_add_column("portfolio_items", "tags", "TEXT", p_cols)
            _safe_add_column("portfolio_items", "workflow", "TEXT", p_cols)
            _safe_add_column("portfolio_items", "format", "VARCHAR(50)", p_cols)
            _safe_add_column("portfolio_items", "aspect_ratio", "VARCHAR(50)", p_cols)

        # 4. Check jobs
        if "jobs" in table_names:
            j_cols = [col["name"] for col in inspector.get_columns("jobs")]
            _safe_add_column("jobs", "budget_inr", "INTEGER DEFAULT 50000", j_cols)
            _safe_add_column("jobs", "budget_range", "VARCHAR(100)", j_cols)
            _safe_add_column("jobs", "commercial_use", "VARCHAR(100) DEFAULT 'Full Commercial Buyout'", j_cols)
            _safe_add_column("jobs", "campaign_requirements", "TEXT", j_cols)
            _safe_add_column("jobs", "content_type", "VARCHAR(100)", j_cols)
            _safe_add_column("jobs", "style", "VARCHAR(100)", j_cols)
            _safe_add_column("jobs", "format", "VARCHAR(50)", j_cols)
            _safe_add_column("jobs", "aspect_ratio", "VARCHAR(50)", j_cols)
            _safe_add_column("jobs", "required_skills", "TEXT", j_cols)
            _safe_add_column("jobs", "required_tools", "TEXT", j_cols)
            _safe_add_column("jobs", "specialization", "VARCHAR(100)", j_cols)

        conn.commit()
