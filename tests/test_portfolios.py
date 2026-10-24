import io
from fastapi import status

def test_upload_portfolio_item_success(client, creator_auth_headers, creator_user):
    file_content = b"<svg><circle r='10'/></svg>"
    file = io.BytesIO(file_content)

    data = {
        "title": "Quantum Running Shoe Commercial",
        "content_type": "Video",
        "description": "High energy cinematic video clip",
        "aspect_ratio": "16:9",
        "format": "MP4",
        "tools_models": "Runway Gen-3, Midjourney v6",
        "skills": "AI Video Generation, Prompt Engineering",
        "specialization": "AI Video"
    }

    res = client.post(
        "/api/portfolio",
        data=data,
        files={"file": ("test_clip.png", file, "image/png")},
        headers=creator_auth_headers
    )

    assert res.status_code == status.HTTP_201_CREATED
    body = res.json()
    assert body["title"] == "Quantum Running Shoe Commercial"
    assert body["content_type"] == "Video"
    assert body["aspect_ratio"] == "16:9"
    assert body["file_path"].startswith("/uploads/creators/")

def test_upload_disallowed_extension_fails(client, creator_auth_headers):
    file = io.BytesIO(b"malicious script")
    data = {
        "title": "Malicious Executable",
        "content_type": "Video"
    }
    res = client.post(
        "/api/portfolio",
        data=data,
        files={"file": ("exploit.exe", file, "application/octet-stream")},
        headers=creator_auth_headers
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "not allowed" in res.json()["detail"]

def test_delete_portfolio_item_owner(client, creator_auth_headers, creator_user):
    file = io.BytesIO(b"<svg>test</svg>")
    data = {"title": "Item to Delete", "content_type": "Image"}
    create_res = client.post(
        "/api/portfolio",
        data=data,
        files={"file": ("sample.png", file, "image/png")},
        headers=creator_auth_headers
    )
    item_id = create_res.json()["id"]

    del_res = client.delete(f"/api/portfolio/{item_id}", headers=creator_auth_headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    get_res = client.get(f"/api/portfolio/{item_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

def test_delete_portfolio_item_unauthorized(client, creator_auth_headers, company_auth_headers):
    file = io.BytesIO(b"<svg>test</svg>")
    data = {"title": "Protected Item", "content_type": "Image"}
    create_res = client.post(
        "/api/portfolio",
        data=data,
        files={"file": ("sample.png", file, "image/png")},
        headers=creator_auth_headers
    )
    item_id = create_res.json()["id"]

    # Company trying to delete creator's item
    del_res = client.delete(f"/api/portfolio/{item_id}", headers=company_auth_headers)
    assert del_res.status_code == status.HTTP_403_FORBIDDEN
