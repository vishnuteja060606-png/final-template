from fastapi import status

def test_get_creator_by_id(client, creator_user):
    profile_id = creator_user.creator_profile.id
    res = client.get(f"/api/creators/{profile_id}")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["display_name"] == "Test Creator"
    assert data["specialization"] == "AI Video"

def test_get_my_creator_profile(client, creator_auth_headers):
    res = client.get("/api/creators/me", headers=creator_auth_headers)
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["display_name"] == "Test Creator"

def test_update_creator_profile_owner(client, creator_auth_headers, creator_user):
    profile_id = creator_user.creator_profile.id
    payload = {
        "display_name": "Updated Creator Name",
        "headline": "Senior AI Director",
        "skills": "AI Video, Motion Design, Runway Gen-3"
    }
    res = client.put(f"/api/creators/{profile_id}", json=payload, headers=creator_auth_headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["display_name"] == "Updated Creator Name"
    assert data["headline"] == "Senior AI Director"

def test_update_creator_profile_unauthorized(client, company_auth_headers, creator_user):
    profile_id = creator_user.creator_profile.id
    payload = {
        "display_name": "Malicious Modification"
    }
    # Company user trying to modify creator's profile
    res = client.put(f"/api/creators/{profile_id}", json=payload, headers=company_auth_headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN
