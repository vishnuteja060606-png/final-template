from typing import List, Tuple, Optional, Any
from app.services.interfaces.base_ranking import BaseRankingService
from app.schemas.advanced import MatchScoreBreakdown, RankedCreatorItem

class MockRankingService(BaseRankingService):
    """
    Day 1 Working Stub for Member 4 & 5.
    Implements 2-stage hard filter and 5-signal deterministic scoring breakdown (Equal 20%).
    """

    def evaluate_eligibility(self, creator: Any, job: Any) -> Tuple[bool, Optional[str]]:
        return (True, None)

    def score_creator_for_brief(self, creator: Any, job: Any) -> MatchScoreBreakdown:
        return MatchScoreBreakdown(
            is_eligible=True,
            exclusion_reason=None,
            total_score=87.5,
            semantic_score=85.0,        # 20% -> 17.0
            tool_overlap_score=90.0,    # 20% -> 18.0
            review_rating_score=92.0,   # 20% -> 18.4
            verification_score=95.0,    # 20% -> 19.0
            view_popularity_score=75.5, # 20% -> 15.1
            style_content_score=88.0,
            trust_signal_score=95.0,
            portfolio_evidence_score=76.5,
            average_review_rating=4.9,
            review_count=12,
            views_count=1450,
            matched_tools=["Runway Gen-3 Alpha", "Midjourney v6", "Topaz Video AI"],
            missing_tools=["ComfyUI Pipeline"],
            verified_badges=["Platform Verified Creator", "Verified Workflow Pipeline"],
            supporting_portfolio_ids=[101, 104]
        )

    def rank_creators_for_brief(self, job_id: int, limit: int = 20) -> List[RankedCreatorItem]:
        breakdown_1 = self.score_creator_for_brief(None, None)
        breakdown_2 = MatchScoreBreakdown(
            is_eligible=True,
            exclusion_reason=None,
            total_score=78.2,
            semantic_score=75.0,
            tool_overlap_score=80.0,
            review_rating_score=80.0,
            verification_score=75.0,
            view_popularity_score=81.0,
            style_content_score=85.0,
            trust_signal_score=70.0,
            portfolio_evidence_score=82.0,
            average_review_rating=4.6,
            review_count=8,
            views_count=980,
            matched_tools=["Kling AI v1.5", "Flux.1 Dev"],
            missing_tools=["Runway Gen-3 Alpha"],
            verified_badges=["Platform Verified Creator"],
            supporting_portfolio_ids=[102]
        )
        return [
            RankedCreatorItem(
                creator_id=1,
                display_name="Elena Rostova",
                specialization="AI Filmmaking & Commercials",
                is_verified=True,
                match_score=87.5,
                breakdown=breakdown_1
            ),
            RankedCreatorItem(
                creator_id=2,
                display_name="Marcus Vance",
                specialization="3D Generative Animation & VFX",
                is_verified=True,
                match_score=78.2,
                breakdown=breakdown_2
            )
        ][:limit]

    def reciprocal_rank_fusion(
        self, keyword_ranked_ids: List[int], vector_ranked_ids: List[int], k: int = 60
    ) -> List[Tuple[int, float]]:
        scores = {}
        for rank, cid in enumerate(keyword_ranked_ids):
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank + 1))
        for rank, cid in enumerate(vector_ranked_ids):
            scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank + 1))
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)
