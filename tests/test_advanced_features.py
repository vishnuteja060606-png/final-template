import pytest
from fastapi.testclient import TestClient

def test_semantic_search_endpoint(client: TestClient):
    response = client.post(
        "/api/v2/search/semantic",
        json={"query": "cinematic hyper-realistic sci-fi video", "entity_type": "creator", "top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "cinematic hyper-realistic sci-fi video"
    assert "results" in data
    assert len(data["results"]) > 0
    assert "similarity_score" in data["results"][0]
    assert data["model_used"] == "bge-small-en-v1.5"

def test_ner_extract_endpoint(client: TestClient):
    response = client.post(
        "/api/v2/ner/extract",
        json={
            "text": "Looking for a creator skilled in Runway Gen-3 and Midjourney to deliver a 9:16 commercial buyout campaign.",
            "source_type": "brief_requirement"
        }
    )
    assert response.status_code == 200
    data = response.json()
    tool_canonicals = [t["canonical_value"] for t in data["tools"]]
    format_canonicals = [f["canonical_value"] for f in data["formats"]]
    assert "Runway Gen-3 Alpha" in tool_canonicals
    assert "Midjourney v6" in tool_canonicals
    assert "9:16 Vertical Reel" in format_canonicals
    assert len(data["licensing"]) > 0

def test_hybrid_search_endpoint(client: TestClient):
    response = client.post(
        "/api/v2/search/hybrid",
        json={"query": "Runway anime animator", "page": 1, "page_size": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert data["fusion_algorithm"] == "Reciprocal Rank Fusion (RRF)"
    if len(data["candidates"]) > 0:
        assert "rrf_score" in data["candidates"][0]

def test_rankings_for_brief_endpoint(client: TestClient):
    response = client.post(
        "/api/v2/rankings/creators-for-brief",
        json={"job_id": 1, "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == 1
    assert "ranked_creators" in data
    assert len(data["ranked_creators"]) > 0
    top = data["ranked_creators"][0]
    assert "match_score" in top
    assert "breakdown" in top
    assert top["breakdown"]["is_eligible"] is True
    assert "semantic_score" in top["breakdown"]

def test_rag_brief_generate_endpoint(client: TestClient):
    response = client.post(
        "/api/v2/briefs/ai-generate",
        json={
            "rough_idea": "We need a 30s perfume commercial with cyber aesthetic and liquid neon",
            "company_context": "Luxury futuristic fragrance brand"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "content_type" in data
    assert "aspect_ratio" in data
    assert "required_tools" in data
    assert len(data["grounding_citations"]) > 0

def test_match_explanation_endpoint(client: TestClient):
    response = client.get("/api/v2/creators/1/explain-match/1")
    assert response.status_code == 200
    data = response.json()
    assert data["creator_id"] == 1
    assert data["job_id"] == 1
    assert "explanation_narrative" in data
    assert "breakdown" in data
    assert len(data["grounded_portfolio_evidence"]) > 0


def test_hard_gate_commercial_buyout_exclusion():
    from app.services.ranking_service import ranking_service
    from app.models.creator import CreatorProfile
    from app.models.job import Job

    creator = CreatorProfile(
        id=99,
        user_id=999,
        display_name="Amateur Creator",
        bio="I create non-commercial only art for personal portfolio and hobby.",
        workflow="Open source hobby experiments (Personal use only)."
    )
    job = Job(
        id=99,
        company_id=1,
        title="Nike Super Bowl Campaign",
        description="Global commercial campaign",
        commercial_use="Full Commercial Buyout"
    )

    is_eligible, reason = ranking_service.evaluate_eligibility(creator, job)
    assert is_eligible is False
    assert "commercial" in reason.lower()

    breakdown = ranking_service.score_creator_for_brief(creator, job)
    assert breakdown.is_eligible is False
    assert breakdown.total_score == 0.0

def test_rrf_math():
    from app.services.ranking_service import ranking_service

    kw_ids = [2, 1, 3]
    vec_ids = [2, 4, 1]
    fused = ranking_service.reciprocal_rank_fusion(kw_ids, vec_ids, k=60)
    fused_dict = dict(fused)

    # Creator 2 is rank 1 in both kw and vec: (1/61) + (1/61)
    expected_c2 = (1.0 / 61.0) + (1.0 / 61.0)
    assert abs(fused_dict[2] - expected_c2) < 1e-5
    # Creator 2 strictly ranks #1
    assert fused[0][0] == 2

def test_ner_provenance_and_normalization():
    from app.services.ner_service import ner_service

    raw_text = "Experienced with MJ v6, gen 3, and comfy ui for 9:16 and 16:9 vertical social reel campaigns."
    result = ner_service.extract_entities(raw_text, source_type="creator_claim")

    tool_map = {t.raw_value: t.canonical_value for t in result.tools}
    assert tool_map.get("mj v6") == "Midjourney v6" or tool_map.get("mj") == "Midjourney v6"
    assert any(t.canonical_value == "Runway Gen-3 Alpha" for t in result.tools)
    assert any(t.canonical_value == "ComfyUI Pipeline" for t in result.tools)
    assert all(t.provenance == "creator_claim" for t in result.tools)
