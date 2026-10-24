from fastapi import status

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
