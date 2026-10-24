from fastapi import status
from app.db.seed import seed_database

def test_healthcheck(client):
    res = client.get("/health")
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["status"] == "healthy"

def test_homepage_render(client, db_session):
    seed_database(db_session)
    res = client.get("/")
    assert res.status_code == status.HTTP_200_OK
    assert "Discover the World" in res.text
    assert "Synapse" in res.text

def test_creators_list_page(client, db_session):
    seed_database(db_session)
    res = client.get("/creators")
    assert res.status_code == status.HTTP_200_OK
    assert "Elena Rostova" in res.text

def test_creator_detail_page(client, db_session):
    seed_database(db_session)
    res = client.get("/creators/1")
    assert res.status_code == status.HTTP_200_OK
    assert "Elena Rostova" in res.text
    assert "AI-Generated Portfolio" in res.text

def test_projects_list_page(client, db_session):
    seed_database(db_session)
    res = client.get("/projects")
    assert res.status_code == status.HTTP_200_OK
    assert "Creative Briefs" in res.text

def test_project_detail_page(client, db_session):
    seed_database(db_session)
    res = client.get("/projects/1")
    assert res.status_code == status.HTTP_200_OK
    assert "Cinematic AI Video Campaign" in res.text

def test_companies_directory_page(client, db_session):
    seed_database(db_session)
    res = client.get("/companies")
    assert res.status_code == status.HTTP_200_OK
    assert "Brands & Creative Agencies" in res.text
    assert "OmniSport Global" in res.text

def test_company_detail_page(client, db_session):
    seed_database(db_session)
    res = client.get("/companies/1")
    assert res.status_code == status.HTTP_200_OK
    assert "OmniSport Global" in res.text

def test_ai_builder_page(client):
    res = client.get("/ai-builder")
    assert res.status_code == status.HTTP_200_OK
    assert "AI Creative Brief Builder" in res.text

def test_creator_dashboard_view(client, creator_user, creator_auth_headers):
    # Set cookie as well for web requests
    token = creator_auth_headers["Authorization"].split(" ")[1]
    client.cookies.set("access_token", f"Bearer {token}")
    res = client.get("/dashboard/creator")
    assert res.status_code == status.HTTP_200_OK
    assert "Creator Studio" in res.text

def test_company_dashboard_view(client, company_user, company_auth_headers):
    token = company_auth_headers["Authorization"].split(" ")[1]
    client.cookies.set("access_token", f"Bearer {token}")
    res = client.get("/dashboard/company")
    assert res.status_code == status.HTTP_200_OK
    assert "Brand Studio" in res.text
