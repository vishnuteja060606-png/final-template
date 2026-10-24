from fastapi import status

def test_create_creative_brief_success(client, company_auth_headers, company_user):
    payload = {
        "title": "Quantum Sneaker 30s Spot",
        "description": "Produce a high end synthetic video commercial for our flagship runner.",
        "campaign_requirements": "1x 30s 16:9 master, 2x 9:16 vertical cuts.",
        "content_type": "Video",
        "style": "Cinematic",
        "format": "MP4",
        "aspect_ratio": "16:9",
        "commercial_use": "Full Buyout",
        "required_skills": "AI Video Generation, Color Grading",
        "required_tools": "Runway Gen-3, Topaz Video AI",
        "specialization": "AI Video",
        "budget_range": "$3,500 - $6,000",
        "status": "published"
    }

    res = client.post("/api/jobs", json=payload, headers=company_auth_headers)
    assert res.status_code == status.HTTP_201_CREATED
    data = res.json()
    assert data["title"] == "Quantum Sneaker 30s Spot"
    assert data["company_id"] == company_user.company_profile.id

def test_creator_cannot_post_brief(client, creator_auth_headers):
    payload = {
        "title": "Unauthorized Brief",
        "description": "Should fail because role is creator."
    }
    res = client.post("/api/jobs", json=payload, headers=creator_auth_headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN

def test_list_published_briefs(client, company_auth_headers):
    payload = {
        "title": "Social Reel Series",
        "description": "10 vertical hooks for TikTok and Reels.",
        "status": "published"
    }
    client.post("/api/jobs", json=payload, headers=company_auth_headers)

    res = client.get("/api/jobs")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert len(data) >= 1
    assert any(j["title"] == "Social Reel Series" for j in data)

def test_update_brief_owner(client, company_auth_headers):
    payload = {
        "title": "Initial Title",
        "description": "Original description for project."
    }
    create_res = client.post("/api/jobs", json=payload, headers=company_auth_headers)
    job_id = create_res.json()["id"]

    update_payload = {"title": "Refined Title", "budget_range": "$4,000"}
    update_res = client.put(f"/api/jobs/{job_id}", json=update_payload, headers=company_auth_headers)
    assert update_res.status_code == status.HTTP_200_OK
    assert update_res.json()["title"] == "Refined Title"
    assert update_res.json()["budget_range"] == "$4,000"

def test_delete_brief_owner(client, company_auth_headers):
    payload = {
        "title": "Brief to Delete",
        "description": "Will be removed."
    }
    create_res = client.post("/api/jobs", json=payload, headers=company_auth_headers)
    job_id = create_res.json()["id"]

    del_res = client.delete(f"/api/jobs/{job_id}", headers=company_auth_headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    get_res = client.get(f"/api/jobs/{job_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
