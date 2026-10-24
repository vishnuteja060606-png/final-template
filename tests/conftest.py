import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.services.auth_service import AuthService

# Use an in-memory SQLite database with StaticPool for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database schema for each test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def creator_user(db_session):
    user = User(
        email="test_creator@example.com",
        password_hash=AuthService.hash_password("password123"),
        role="creator"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CreatorProfile(
        user_id=user.id,
        display_name="Test Creator",
        headline="AI Filmmaker",
        specialization="AI Video",
        skills="AI Video Generation, Prompt Engineering",
        tools_models="Runway Gen-3, Midjourney v6"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return user

@pytest.fixture
def company_user(db_session):
    user = User(
        email="test_company@example.com",
        password_hash=AuthService.hash_password("password123"),
        role="company"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CompanyProfile(
        user_id=user.id,
        company_name="Test Brand Inc",
        industry="Footwear"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return user

@pytest.fixture
def creator_token(creator_user):
    return AuthService.create_access_token(
        data={"sub": str(creator_user.id), "role": creator_user.role, "email": creator_user.email}
    )

@pytest.fixture
def company_token(company_user):
    return AuthService.create_access_token(
        data={"sub": str(company_user.id), "role": company_user.role, "email": company_user.email}
    )

@pytest.fixture
def creator_auth_headers(creator_token):
    return {"Authorization": f"Bearer {creator_token}"}

@pytest.fixture
def company_auth_headers(company_token):
    return {"Authorization": f"Bearer {company_token}"}
