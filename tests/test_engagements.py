from fastapi import status

def test_create_and_manage_engagement(client, company_auth_headers, creator_auth_headers, creator_user, company_user):
    # 1. Company sends proposal to creator
    payload = {
        "creator_id": creator_user.creator_profile.id,
        "message": "We want to hire you for an AI commercial campaign.",
        "proposed_budget": "$4,500"
    }
    create_res = client.post("/api/engagements", json=payload, headers=company_auth_headers)
    assert create_res.status_code == status.HTTP_201_CREATED
    eng_id = create_res.json()["id"]
    assert create_res.json()["status"] == "pending"

    # 2. Creator checks incoming engagements
    my_engs_res = client.get("/api/engagements/my", headers=creator_auth_headers)
    assert my_engs_res.status_code == status.HTTP_200_OK
    data = my_engs_res.json()
    assert len(data) >= 1
    assert any(e["id"] == eng_id for e in data)

    # 3. Creator accepts the proposal
    status_update_res = client.put(
        f"/api/engagements/{eng_id}/status",
        json={"status": "accepted"},
        headers=creator_auth_headers
    )
    assert status_update_res.status_code == status.HTTP_200_OK
    assert status_update_res.json()["status"] == "accepted"

def test_creator_cannot_initiate_engagement(client, creator_auth_headers, creator_user):
    payload = {
        "creator_id": creator_user.creator_profile.id,
        "message": "Creator trying to send proposal"
    }
    res = client.post("/api/engagements", json=payload, headers=creator_auth_headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN
