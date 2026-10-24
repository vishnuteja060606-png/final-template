from fastapi import status, Depends
from app.api.auth import require_creator, require_company
from app.models.user import User

def test_register_creator_success(client):
    payload = {
        "email": "new_creator@domain.com",
        "password": "securepassword",
        "role": "creator",
        "name": "Jane Doe"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "creator"
    assert data["profile_id"] is not None

def test_register_company_success(client):
    payload = {
        "email": "agency@domain.com",
        "password": "securepassword",
        "role": "company",
        "name": "Apex Creative"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["role"] == "company"

def test_register_duplicate_email_fails(client, creator_user):
    payload = {
        "email": creator_user.email,
        "password": "anotherpassword",
        "role": "creator",
        "name": "Duplicate User"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in res.json()["detail"]

def test_login_success(client, creator_user):
    payload = {
        "email": creator_user.email,
        "password": "password123"
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert "access_token" in data
    assert data["user_id"] == creator_user.id

def test_login_invalid_password(client, creator_user):
    payload = {
        "email": creator_user.email,
        "password": "wrongpassword"
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_me_authenticated(client, creator_auth_headers, creator_user):
    res = client.get("/api/auth/me", headers=creator_auth_headers)
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["email"] == creator_user.email

def test_get_me_unauthenticated(client):
    res = client.get("/api/auth/me")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

def test_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == status.HTTP_200_OK

def test_session_endpoint(client, creator_user, creator_auth_headers, company_user, company_auth_headers):
    # Unauthenticated session check
    res_unauth = client.get("/api/auth/session")
    assert res_unauth.status_code == status.HTTP_200_OK
    data_unauth = res_unauth.json()
    assert data_unauth["authenticated"] is False
    assert data_unauth["role"] is None

    # Creator session check
    res_creator = client.get("/api/auth/session", headers=creator_auth_headers)
    assert res_creator.status_code == status.HTTP_200_OK
    data_creator = res_creator.json()
    assert data_creator["authenticated"] is True
    assert data_creator["role"] == "creator"
    assert data_creator["profile_id"] == creator_user.creator_profile.id

    # Company session check
    res_comp = client.get("/api/auth/session", headers=company_auth_headers)
    assert res_comp.status_code == status.HTTP_200_OK
    data_comp = res_comp.json()
    assert data_comp["authenticated"] is True
    assert data_comp["role"] == "company"
    assert data_comp["profile_id"] == company_user.company_profile.id

def test_role_based_navbar_enforcement_visitor(client):
    """Visitor must see all discovery links: Discover Creators, Brands & Companies, Creative Briefs."""
    client.cookies.clear()
    res = client.get("/")
    assert res.status_code == status.HTTP_200_OK
    html = res.text
    assert 'id="navDiscoverCreators"' in html
    assert 'id="navBrandsCompanies"' in html
    assert 'id="navCreativeBriefs"' in html
    assert 'id="navLoginBtn"' in html

def test_role_based_navbar_enforcement_creator(client, creator_user):
    """When creator is logged in: Hide 'Discover Creators', show 'Brands & Companies'."""
    login_res = client.post("/api/auth/login", json={"email": creator_user.email, "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    client.cookies.set("access_token", f"Bearer {token}")

    res = client.get("/")
    assert res.status_code == status.HTTP_200_OK
    html = res.text
    # Creator must NOT see Discover Creators link
    assert 'id="navDiscoverCreators"' not in html
    # Creator MUST see Brands & Companies link
    assert 'id="navBrandsCompanies"' in html
    # Creator MUST see their studio/portfolio link
    assert 'id="navCreatorDashboard"' in html

def test_role_based_navbar_enforcement_company(client, company_user):
    """When company is logged in: Hide 'Brands & Companies', show 'Discover Creators'."""
    login_res = client.post("/api/auth/login", json={"email": company_user.email, "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    client.cookies.set("access_token", f"Bearer {token}")

    res = client.get("/")
    assert res.status_code == status.HTTP_200_OK
    html = res.text
    # Company MUST see Discover Creators link
    assert 'id="navDiscoverCreators"' in html
    # Company must NOT see Brands & Companies link
    assert 'id="navBrandsCompanies"' not in html
    # Company must NOT see Creator studio link
    assert 'id="navCreatorDashboard"' not in html
