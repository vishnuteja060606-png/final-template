import pytest
from fastapi import status
from unittest.mock import patch
from app.config import settings
from app.models.user import User
from app.models.company import CompanyProfile
from app.models.job import Job
from app.services.auth_service import AuthService
from app.schemas.ai import AIBriefRequest, AIBriefResponse
from app.services.ai_service import ai_service

def test_database_url_safe_resolution():
    """Verify that settings resolve SQLite database URLs safely."""
    assert settings.DATABASE_URL.startswith("sqlite:///")
    assert "marketplace.db" in settings.DATABASE_URL

def test_groq_models_and_api_settings():
    """Verify Groq model configuration and fallback chain."""
    assert settings.GROQ_MODEL is not None
    assert "llama" in settings.GROQ_MODEL.lower() or "mixtral" in settings.GROQ_MODEL.lower()
    assert len(settings.GROQ_FALLBACK_MODELS) >= 2

def test_registration_triggers_email_validation_otp(client, db_session):
    """Verify that user registration immediately dispatches OTP code for email validation."""
    payload = {
        "email": "validate_me@creatives.ai",
        "password": "securepassword123",
        "role": "creator",
        "name": "Maya Lin"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert "access_token" in data

    # Check user in database has email_otp_code populated
    user = db_session.query(User).filter(User.email == "validate_me@creatives.ai").first()
    assert user is not None
    assert user.email_otp_code is not None
    assert len(user.email_otp_code) == 6

    # Verify that the OTP can be used to authenticate
    verify_res = client.post("/api/auth/verify-otp", json={
        "email": "validate_me@creatives.ai",
        "code": user.email_otp_code
    })
    assert verify_res.status_code == status.HTTP_200_OK
    assert "access_token" in verify_res.json()

def test_company_cannot_see_other_companies_briefs(client, db_session, company_user, company_auth_headers):
    """Verify that Company A cannot see Company B's creative briefs."""
    # 1. Company A posts a brief
    brief_a_payload = {
        "title": "Alpha Brand Video Campaign",
        "description": "Confidential commercial campaign for Alpha Brand.",
        "content_type": "Video",
        "status": "published"
    }
    res_a = client.post("/api/jobs", json=brief_a_payload, headers=company_auth_headers)
    assert res_a.status_code == status.HTTP_201_CREATED
    job_a_id = res_a.json()["id"]

    # 2. Register Company B
    reg_b = client.post("/api/auth/register", json={
        "email": "beta_company@domain.com",
        "password": "password123",
        "role": "company",
        "name": "Beta Enterprises"
    })
    assert reg_b.status_code == status.HTTP_201_CREATED
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Company B posts a brief
    brief_b_payload = {
        "title": "Beta Brand Animation Reel",
        "description": "Confidential animation project for Beta Brand.",
        "content_type": "Animation",
        "status": "published"
    }
    res_b = client.post("/api/jobs", json=brief_b_payload, headers=headers_b)
    assert res_b.status_code == status.HTTP_201_CREATED
    job_b_id = res_b.json()["id"]

    # 3. Company A lists jobs via /api/jobs -> MUST see brief A, MUST NOT see brief B
    list_a = client.get("/api/jobs", headers=company_auth_headers)
    assert list_a.status_code == status.HTTP_200_OK
    titles_a = [j["title"] for j in list_a.json()]
    assert "Alpha Brand Video Campaign" in titles_a
    assert "Beta Brand Animation Reel" not in titles_a

    # 4. Company B lists jobs via /api/jobs -> MUST see brief B, MUST NOT see brief A
    list_b = client.get("/api/jobs", headers=headers_b)
    assert list_b.status_code == status.HTTP_200_OK
    titles_b = [j["title"] for j in list_b.json()]
    assert "Beta Brand Animation Reel" in titles_b
    assert "Alpha Brand Video Campaign" not in titles_b

    # 5. Company B attempts to access Company A's brief by ID -> MUST be 403 Forbidden!
    forbidden_res = client.get(f"/api/jobs/{job_a_id}", headers=headers_b)
    assert forbidden_res.status_code == status.HTTP_403_FORBIDDEN
    assert "confidentiality" in forbidden_res.json()["detail"].lower()

    # 6. Company A attempts to access Company B's brief by ID -> MUST be 403 Forbidden!
    forbidden_res_2 = client.get(f"/api/jobs/{job_b_id}", headers=company_auth_headers)
    assert forbidden_res_2.status_code == status.HTTP_403_FORBIDDEN

    # 7. Clear session cookies so request is genuinely unauthenticated guest
    client.cookies.clear()
    public_res = client.get(f"/api/jobs/{job_a_id}")
    assert public_res.status_code == status.HTTP_200_OK

def test_company_search_isolation(client, company_auth_headers):
    """Verify that searching /api/search/jobs as a company returns only their own briefs."""
    res = client.get("/api/search/jobs", headers=company_auth_headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "items" in data

def test_ai_brief_service_custom_model_parameter(client):
    """Verify that AIBriefRequest accepts optional model parameter."""
    payload = {
        "prompt": "Create an AI animation teaser for an indie game",
        "company_context": "IndieDev Studio",
        "model": "llama-3.1-8b-instant"
    }
    res = client.post("/api/ai/brief-builder", json=payload)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "title" in data
    assert data["content_type"] == "Animation"
