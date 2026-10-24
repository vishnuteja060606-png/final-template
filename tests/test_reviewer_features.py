import pytest
from fastapi import status
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.models.portfolio import PortfolioItem
from app.models.review import CreatorReview
from app.models.connection import CreatorConnection
from app.services.creator_service import creator_service

def test_company_review_submission_and_metrics(client, db_session, company_user, creator_user):
    """
    Reviewer Requirement: Company can give reviews for creators.
    """
    creator = creator_user.creator_profile
    assert creator is not None

    # Login as company
    login_res = client.post("/api/auth/login", json={"email": company_user.email, "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Submit review
    review_payload = {
        "rating": 5,
        "project_title": "Quantum Sneaker Hero Ad",
        "comment": "Outstanding 4K Runway Gen-3 camera direction with pristine lighting.",
        "tools_used": "Runway Gen-3 + Topaz Video AI",
        "is_verified_engagement": True
    }
    res = client.post(f"/creators/{creator.id}/reviews", json=review_payload, headers=headers)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["rating"] == 5
    assert data["project_title"] == "Quantum Sneaker Hero Ad"
    assert data["is_verified_engagement"] is True

    # Retrieve reviews list
    list_res = client.get(f"/creators/{creator.id}/reviews")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total_reviews"] >= 1
    assert list_data["average_rating"] == 5.0

def test_creator_cannot_submit_company_review(client, creator_user):
    """Only companies can review creators."""
    login_res = client.post("/api/auth/login", json={"email": creator_user.email, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/creators/1/reviews", json={
        "rating": 4,
        "project_title": "Invalid Attempt",
        "comment": "Creators should not be able to review other creators via company review."
    }, headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

def test_creator_connections_flow(client, db_session, creator_user):
    """
    Reviewer Requirement: Creator connections (mutual networking).
    """
    # Create second creator user
    user2 = User(email="creator2@example.com", password_hash=creator_user.password_hash, role="creator")
    db_session.add(user2)
    db_session.commit()
    profile2 = CreatorProfile(
        user_id=user2.id,
        display_name="Maya Lin",
        specialization="AI Audio",
        status="draft"
    )
    db_session.add(profile2)
    db_session.commit()

    # Login as creator 1
    login_res = client.post("/api/auth/login", json={"email": creator_user.email, "password": "password123"})
    token1 = login_res.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # Cannot connect with self
    self_res = client.post(f"/api/creators/{creator_user.creator_profile.id}/connect", headers=headers1)
    assert self_res.status_code == status.HTTP_400_BAD_REQUEST

    # Send connection request to profile2
    connect_res = client.post(f"/api/creators/{profile2.id}/connect", headers=headers1)
    assert connect_res.status_code == status.HTTP_201_CREATED
    conn_data = connect_res.json()
    assert conn_data["status"] == "pending"
    conn_id = conn_data["id"]

    # Login as creator 2 and accept
    login_res2 = client.post("/api/auth/login", json={"email": "creator2@example.com", "password": "password123"})
    token2 = login_res2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    accept_res = client.post(f"/api/connections/{conn_id}/status", json={"action": "accept"}, headers=headers2)
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "accepted"

    # Verify connection summary
    summary_res = client.get(f"/api/creators/{profile2.id}/connections")
    assert summary_res.status_code == 200
    assert summary_res.json()["total_connections"] == 1

def test_mandatory_two_uploads_and_pinning(client, db_session, creator_user):
    """
    Reviewer Requirements:
    - At least 2 uploads mandatory for published status.
    - Creator can pin their best work (up to 3).
    """
    creator = creator_user.creator_profile
    assert creator is not None

    # Check status transitions
    creator_service.refresh_publication_status(db_session, creator.id)
    # If no portfolio items, status is draft
    assert creator.published_uploads_count < 2
    assert creator.status == "draft"

    # Add 2 items
    p1 = PortfolioItem(
        creator_id=creator.id,
        title="Work 1",
        file_path="/uploads/test1.png",
        original_filename="test1.png",
        mime_type="image/png",
        file_size=500,
        content_type="Image"
    )
    p2 = PortfolioItem(
        creator_id=creator.id,
        title="Work 2",
        file_path="/uploads/test2.png",
        original_filename="test2.png",
        mime_type="image/png",
        file_size=500,
        content_type="Image"
    )
    p3 = PortfolioItem(
        creator_id=creator.id,
        title="Work 3",
        file_path="/uploads/test3.png",
        original_filename="test3.png",
        mime_type="image/png",
        file_size=500,
        content_type="Image"
    )
    p4 = PortfolioItem(
        creator_id=creator.id,
        title="Work 4",
        file_path="/uploads/test4.png",
        original_filename="test4.png",
        mime_type="image/png",
        file_size=500,
        content_type="Image"
    )
    db_session.add_all([p1, p2, p3, p4])
    db_session.commit()

    # Now publication status should become 'published'
    new_status = creator_service.refresh_publication_status(db_session, creator.id)
    assert new_status == "published"
    assert creator.is_eligible_to_publish is True

    # Pin items 1, 2, 3
    login_res = client.post("/api/auth/login", json={"email": creator_user.email, "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    for item in [p1, p2, p3]:
        pin_res = client.post(f"/api/creators/portfolio/{item.id}/pin", json={"is_pinned": True}, headers=headers)
        assert pin_res.status_code == 200
        assert pin_res.json()["is_pinned"] is True

    # Attempt to pin 4th item -> should fail (max 3 items limit)
    pin_fourth = client.post(f"/api/creators/portfolio/{p4.id}/pin", json={"is_pinned": True}, headers=headers)
    assert pin_fourth.status_code == status.HTTP_400_BAD_REQUEST
    assert "maximum of 3" in pin_fourth.json()["detail"]

    # Unpin item 1
    unpin_res = client.post(f"/api/creators/portfolio/{p1.id}/pin", json={"is_pinned": False}, headers=headers)
    assert unpin_res.status_code == 200
    assert unpin_res.json()["is_pinned"] is False
