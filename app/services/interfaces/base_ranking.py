from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
from app.schemas.advanced import MatchScoreBreakdown, RankedCreatorItem

class BaseRankingService(ABC):
    """
    Abstract Interface for Deterministic Creator–Brief Ranking Engine & Hybrid Search Fusion.
    Assigned to: Member 4 (Hybrid Search combined with Member 3)
    Technology: 2-Stage Pipeline (Hard Gates + 5-Signal Normalized Formula) & RRF
    """

    @abstractmethod
    def evaluate_eligibility(self, creator: Any, job: Any) -> Tuple[bool, Optional[str]]:
        """
        Stage 1 Hard Filter:
        Verifies non-negotiable requirements:
        - Commercial use buyout rights
        - Deliverable format & aspect ratio capability
        - Availability status
        Returns: (True, None) if eligible, or (False, "Exclusion reason")
        """
        pass

    @abstractmethod
    def score_creator_for_brief(self, creator: Any, job: Any) -> MatchScoreBreakdown:
        """
        Stage 2 Scoring Formula (0 - 100):
        - Semantic Relevancy: 30%
        - Tool / Model Overlap: 25%
        - Style & Content Compatibility: 20%
        - Trust & Verification Signals: 15%
        - Portfolio Evidence: 10%
        Returns component-level breakdown and supporting proof.
        """
        pass

    @abstractmethod
    def rank_creators_for_brief(self, job_id: int, limit: int = 20) -> List[RankedCreatorItem]:
        """
        Retrieve all creators, run Stage 1 filter, score eligible candidates via Stage 2,
        and return sorted descending by total_score.
        """
        pass

    @abstractmethod
    def reciprocal_rank_fusion(
        self,
        keyword_ranked_ids: List[int],
        vector_ranked_ids: List[int],
        k: int = 60
    ) -> List[Tuple[int, float]]:
        """
        Merge candidate lists using standard RRF: RRF_score = sum(1 / (k + rank_i)).
        """
        pass
