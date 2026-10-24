from fastapi import status
from unittest.mock import patch
from app.schemas.ai import AIBriefRequest, AIBriefResponse
from app.services.ai_service import ai_service

def test_ai_brief_fallback_when_no_groq_key(client):
    # Tests that when GROQ_API_KEY is unset or empty, the service falls back gracefully
    payload = {
        "prompt": "I need a short AI video campaign for running shoes with impossible camera angles in 16:9",
        "company_context": "OmniSport"
    }
    res = client.post("/api/ai/brief-builder", json=payload)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["content_type"] == "Video"
    assert data["aspect_ratio"] == "16:9"
    assert "Runway" in data["required_tools"]
    assert "title" in data
    assert "description" in data
    assert "campaign_requirements" in data

def test_ai_brief_with_mocked_groq_response(client):
    mock_brief_data = {
        "title": "Quantum Leap Running Campaign",
        "description": "A high-fidelity cinematic video spotlighting futuristic footwear.",
        "campaign_requirements": "30s 16:9 4K master with sound design.",
        "content_type": "Video",
        "style": "Hyper-realistic Cyberpunk",
        "format": "MP4",
        "aspect_ratio": "16:9",
        "commercial_use": "Full Commercial Buyout",
        "required_skills": "AI Video Generation, Topaz Upscaling",
        "required_tools": "Runway Gen-3, Kling AI",
        "specialization": "AI Video",
        "budget_range": "$5,000",
        "source": "groq"
    }

    with patch.object(ai_service, "generate_brief", return_value=AIBriefResponse(**mock_brief_data)):
        res = client.post("/api/ai/brief-builder", json={"prompt": "Produce a shoe spot"})
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["title"] == "Quantum Leap Running Campaign"
        assert data["source"] == "groq"
