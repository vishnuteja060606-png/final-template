import pytest
from app.models.company import CompanyProfile
from app.models.company_view import CompanyProfileView
from app.services.company_service import company_service

def test_list_companies_api(client, company_user):
    # Retrieve the company profile for the test brand
    response = client.get("/api/companies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["company_name"] == "Test Brand Inc"
    assert "views_count" in data[0]

def test_search_companies_by_keyword(client, company_user):
    response = client.get("/api/companies?query=Brand")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("Brand" in c["company_name"] for c in data)

    response_empty = client.get("/api/companies?query=NonExistentBrand12345")
    assert response_empty.status_code == 200
    assert len(response_empty.json()) == 0

def test_creator_check_company_profile_reflects_in_db(client, db_session, creator_user, creator_auth_headers, company_user):
    company_profile = db_session.query(CompanyProfile).filter(CompanyProfile.user_id == company_user.id).first()
    assert company_profile is not None
    initial_views = company_profile.views_count

    # Creator checks the company profile via API
    response = client.post(
        f"/api/companies/{company_profile.id}/check",
        headers=creator_auth_headers
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["company_id"] == company_profile.id
    assert res_data["views_count"] == initial_views + 1
    assert res_data["checked_by_creator"] == creator_user.creator_profile.display_name
    assert res_data["checked_at"] is not None

    # Verify directly in DB that CompanyProfile.views_count was incremented
    db_session.expire_all()
    updated_company = db_session.query(CompanyProfile).filter(CompanyProfile.id == company_profile.id).first()
    assert updated_company.views_count == initial_views + 1

    # Verify directly in DB that CompanyProfileView record was saved
    view_records = db_session.query(CompanyProfileView).filter(
        CompanyProfileView.company_id == company_profile.id
    ).all()
    assert len(view_records) == 1
    view_record = view_records[0]
    assert view_record.viewer_user_id == creator_user.id
    assert view_record.creator_id == creator_user.creator_profile.id
    assert view_record.viewer_role == "creator"
    assert view_record.checked_at is not None

def test_company_profile_html_page_check_reflects_in_db(client, db_session, creator_user, company_user):
    company_profile = db_session.query(CompanyProfile).filter(CompanyProfile.user_id == company_user.id).first()
    assert company_profile is not None
    initial_views = company_profile.views_count

    # Simulate creator logged-in browsing company detail page
    token_res = client.post(
        "/api/auth/login",
        json={"email": creator_user.email, "password": "password123"}
    )
    assert token_res.status_code == 200
    token = token_res.json()["access_token"]
    client.cookies.set("access_token", token)

    # Creator visits company detail page
    response = client.get(f"/companies/{company_profile.id}")
    assert response.status_code == 200
    assert "Test Brand Inc" in response.text
    assert "Creator Profile Check Active" in response.text

    # Verify DB reflection
    db_session.expire_all()
    updated_company = db_session.query(CompanyProfile).filter(CompanyProfile.id == company_profile.id).first()
    assert updated_company.views_count == initial_views + 1

    # Verify creator dashboard displays the checked company
    creator_dash = client.get("/dashboard/creator")
    assert creator_dash.status_code == 200
    assert "Companies &amp; Brands You&#39;ve Checked" in creator_dash.text or "Companies & Brands You've Checked" in creator_dash.text
    assert "Test Brand Inc" in creator_dash.text

    # Log in as company user and check company dashboard shows the creator check
    comp_token = client.post(
        "/api/auth/login",
        json={"email": company_user.email, "password": "password123"}
    ).json()["access_token"]
    client.cookies.set("access_token", comp_token)

    comp_dash = client.get("/dashboard/company")
    assert comp_dash.status_code == 200
    assert "Creator Profile Checks" in comp_dash.text
    assert creator_user.creator_profile.display_name in comp_dash.text
