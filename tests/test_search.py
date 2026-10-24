from fastapi import status
from app.models.portfolio import PortfolioItem

def test_search_creators_by_tool(client, creator_user):
    res = client.get("/api/search/creators?tool=Runway")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total"] >= 1
    assert any(c["display_name"] == "Test Creator" for c in data["items"])

def test_search_creators_by_specialization(client, creator_user):
    res = client.get("/api/search/creators?specialization=AI+Video")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total"] >= 1
    assert any(c["specialization"] == "AI Video" for c in data["items"])

def test_search_creators_by_keyword_query(client, creator_user):
    res = client.get("/api/search/creators?query=filmmaker")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total"] >= 1

def test_search_creators_case_normalization(client, creator_user):
    res1 = client.get("/api/search/creators?tool=runway")
    res2 = client.get("/api/search/creators?tool=RUNWAY")
    assert res1.json()["total"] == res2.json()["total"]

def test_search_creators_empty_results(client):
    res = client.get("/api/search/creators?query=nonexistent_query_xyz_12345")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["message"] is not None

def test_search_creators_by_portfolio_metadata(client, creator_user, db_session):
    # Add a portfolio item with aspect ratio 9:16
    item = PortfolioItem(
        creator_id=creator_user.creator_profile.id,
        title="Vertical Reel Teaser",
        description="Reels viral clip",
        file_path="/uploads/test.png",
        original_filename="test.png",
        mime_type="image/png",
        file_size=100,
        content_type="Video",
        aspect_ratio="9:16",
        format="MP4",
        tools_models="Kling AI",
        skills="Short-form"
    )
    db_session.add(item)
    db_session.commit()

    res = client.get("/api/search/creators?aspect_ratio=9:16")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total"] >= 1
    assert any(c["id"] == creator_user.creator_profile.id for c in data["items"])

def test_search_jobs_by_filter(client, company_auth_headers):
    payload = {
        "title": "Anime Concept Pilot",
        "description": "Produce a pilot animation reel.",
        "content_type": "Animation",
        "specialization": "AI Animation",
        "status": "published"
    }
    client.post("/api/jobs", json=payload, headers=company_auth_headers)

    res = client.get("/api/search/jobs?content_type=Animation")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["total"] >= 1
    assert any(j["content_type"] == "Animation" for j in data["items"])
