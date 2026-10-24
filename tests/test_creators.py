from fastapi import status
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.portfolio import PortfolioItem
from app.services.creator_service import creator_service

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

def test_creator_views_tracking_session_deduplication(client, creator_user):
    """
    Reviewer Requirement: View tracking with session de-duplication.
    """
    creator_service.clear_view_cache()
    profile_id = creator_user.creator_profile.id

    # 1. First visit with session-alpha
    res1 = client.get(f"/api/creators/{profile_id}", headers={"x-session-id": "session-alpha"})
    assert res1.status_code == status.HTTP_200_OK
    views1 = res1.json()["views_count"]
    assert views1 >= 1

    # 2. Second visit with the same session-alpha (refresh spam) -> views should NOT increment
    res2 = client.get(f"/api/creators/{profile_id}", headers={"x-session-id": "session-alpha"})
    assert res2.status_code == status.HTTP_200_OK
    views2 = res2.json()["views_count"]
    assert views2 == views1

    # 3. Third visit with different session-beta -> views SHOULD increment
    res3 = client.get(f"/api/creators/{profile_id}", headers={"x-session-id": "session-beta"})
    assert res3.status_code == status.HTTP_200_OK
    views3 = res3.json()["views_count"]
    assert views3 == views1 + 1

def test_portfolio_item_views_tracking_session_deduplication(client, db_session, creator_user):
    """
    Reviewer Requirement: Portfolio item view tracking with session de-duplication.
    """
    creator_service.clear_view_cache()
    profile = creator_user.creator_profile

    item = PortfolioItem(
        creator_id=profile.id,
        title="Session Test Clip",
        file_path="/uploads/test_clip.mp4",
        original_filename="test_clip.mp4",
        mime_type="video/mp4",
        file_size=1024,
        content_type="Video",
        views_count=0
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    # First view with session-1
    res1 = client.post(f"/api/creators/portfolio/{item.id}/view", headers={"x-session-id": "sess-1"})
    assert res1.status_code == status.HTTP_200_OK
    assert res1.json()["views_count"] == 1

    # Repeat view in same session -> de-duplicated
    res2 = client.post(f"/api/creators/portfolio/{item.id}/view", headers={"x-session-id": "sess-1"})
    assert res2.status_code == status.HTTP_200_OK
    assert res2.json()["views_count"] == 1

    # Distinct session -> incremented
    res3 = client.post(f"/api/creators/portfolio/{item.id}/view", headers={"x-session-id": "sess-2"})
    assert res3.status_code == status.HTTP_200_OK
    assert res3.json()["views_count"] == 2

def test_cannot_pin_another_creators_portfolio_item(client, db_session, creator_user):
    """
    A creator cannot pin an item belonging to another creator.
    """
    # Create second creator
    user2 = User(email="other_creator@example.com", password_hash=creator_user.password_hash, role="creator")
    db_session.add(user2)
    db_session.commit()
    profile2 = CreatorProfile(user_id=user2.id, display_name="Other Artist", status="draft")
    db_session.add(profile2)
    db_session.commit()

    item_other = PortfolioItem(
        creator_id=profile2.id,
        title="Other Artist's Piece",
        file_path="/uploads/piece.png",
        original_filename="piece.png",
        mime_type="image/png",
        file_size=500,
        content_type="Image"
    )
    db_session.add(item_other)
    db_session.commit()

    login_res = client.post("/api/auth/login", json={"email": creator_user.email, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # creator_user tries to pin item_other -> should fail with 403 Forbidden
    res = client.post(f"/api/creators/portfolio/{item_other.id}/pin", json={"is_pinned": True}, headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

def test_creator_connection_pending_endpoints_and_rejection(client, db_session, creator_user):
    """
    Tests pending connection retrieval, sender restriction on accept, and reject status.
    """
    # Create second creator
    user2 = User(email="networking_creator@example.com", password_hash=creator_user.password_hash, role="creator")
    db_session.add(user2)
    db_session.commit()
    profile2 = CreatorProfile(user_id=user2.id, display_name="Networking Creator", status="draft")
    db_session.add(profile2)
    db_session.commit()

    # Creator 1 logs in
    login1 = client.post("/api/auth/login", json={"email": creator_user.email, "password": "password123"})
    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Creator 1 sends request to Creator 2
    req_res = client.post(f"/api/creators/{profile2.id}/connect", headers=headers1)
    assert req_res.status_code == status.HTTP_201_CREATED
    conn_id = req_res.json()["id"]

    # Creator 1 checks sent pending requests
    sent_res = client.get("/api/connections/sent", headers=headers1)
    assert sent_res.status_code == status.HTTP_200_OK
    assert len(sent_res.json()) >= 1
    assert sent_res.json()[0]["receiver_id"] == profile2.id

    # Creator 1 cannot accept their own outgoing request
    bad_accept = client.post(f"/api/connections/{conn_id}/status", json={"action": "accept"}, headers=headers1)
    assert bad_accept.status_code == status.HTTP_403_FORBIDDEN

    # Creator 2 logs in and checks incoming pending requests
    login2 = client.post("/api/auth/login", json={"email": "networking_creator@example.com", "password": "password123"})
    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    incoming_res = client.get("/api/connections/pending", headers=headers2)
    assert incoming_res.status_code == status.HTTP_200_OK
    assert len(incoming_res.json()) >= 1
    assert incoming_res.json()[0]["requester_id"] == creator_user.creator_profile.id

    # Creator 2 rejects the request
    reject_res = client.post(f"/api/connections/{conn_id}/status", json={"action": "reject"}, headers=headers2)
    assert reject_res.status_code == status.HTTP_200_OK
    assert reject_res.json()["status"] == "rejected"
