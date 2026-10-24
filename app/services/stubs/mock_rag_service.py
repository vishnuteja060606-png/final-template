from typing import Optional, Dict, Any
from app.services.interfaces.base_rag import BaseRAGService
from app.schemas.advanced import (
    RAGBriefGenerateResponse,
    MatchExplanationResponse,
    MatchScoreBreakdown,
)

class MockRAGService(BaseRAGService):
    """
    Day 1 Working Stub for Member 4.
    Synthesizes structured briefs and grounded match explanations with citations.
    """

    def generate_structured_brief(
        self,
        rough_idea: str,
        company_context: Optional[str] = None
    ) -> RAGBriefGenerateResponse:
        idea_clean = rough_idea.strip()
        title = f"AI Production Brief: {idea_clean[:35]}..." if idea_clean else "New AI Creative Brief"
        return RAGBriefGenerateResponse(
            title=title,
            content_type="Video",
            style="Cinematic Cyberpunk / Photorealistic",
            format="MP4 (ProRes on request)",
            aspect_ratio="16:9",
            commercial_use="Full Commercial Buyout",
            required_skills=["AI Video Generation", "Prompt Engineering", "Color Grading", "Upscaling"],
            required_tools=["Runway Gen-3 Alpha", "Midjourney v6", "Topaz Video AI"],
            campaign_requirements="Storyboard review required before high-res video rendering. Deliver in 4K 60fps.",
            budget_range="$2,500 - $5,000",
            grounding_citations=[
                "Catalog Standard: Runway Gen-3 Alpha Video Pipeline",
                "Historical Brief #14: High-End Cyber Commercial Benchmark"
            ]
        )

    def explain_creator_match(
        self,
        creator_id: int,
        job_id: int
    ) -> MatchExplanationResponse:
        breakdown = MatchScoreBreakdown(
            is_eligible=True,
            exclusion_reason=None,
            total_score=87.5,
            semantic_score=85.0,
            tool_overlap_score=90.0,
            style_content_score=88.0,
            trust_signal_score=95.0,
            portfolio_evidence_score=76.5,
            matched_tools=["Runway Gen-3 Alpha", "Midjourney v6"],
            missing_tools=["ComfyUI Pipeline"],
            verified_badges=["Platform Verified Creator", "Verified Workflow Pipeline"],
            supporting_portfolio_ids=[101, 104]
        )
        narrative = (
            f"Creator #{creator_id} is ranked top match for Brief #{job_id}. "
            f"They possess verified skills in Runway Gen-3 and Midjourney v6 matching 100% of required generative tools. "
            f"Their portfolio project #101 demonstrated 4K cinematic delivery matching your requested 16:9 aspect ratio and full commercial buyout rights."
        )
        return MatchExplanationResponse(
            creator_id=creator_id,
            job_id=job_id,
            explanation_narrative=narrative,
            breakdown=breakdown,
            grounded_portfolio_evidence=[
                {
                    "portfolio_id": 101,
                    "title": "Neon Horizons — Cyber Teaser",
                    "aspect_ratio": "16:9",
                    "tools_used": "Runway Gen-3, Midjourney v6"
                }
            ]
        )
