from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.schemas.advanced import RAGBriefGenerateResponse, MatchExplanationResponse

class BaseRAGService(ABC):
    """
    Abstract Interface for Retrieval-Augmented Generation (RAG).
    Assigned to: Member 4
    Technology: DB Context Retrieval + Groq LLM (llama-3.3-70b-versatile) + Pydantic Schema Validation
    """

    @abstractmethod
    def generate_structured_brief(
        self,
        rough_idea: str,
        company_context: Optional[str] = None
    ) -> RAGBriefGenerateResponse:
        """
        1. Retrieve canonical toolstacks, aspect ratios, and brief templates from DB/catalog.
        2. Prompt Groq LLM to synthesize a full structured creative brief.
        3. Enforce zero hallucinations: Validate all output tools and formats against canonical models.
        """
        pass

    @abstractmethod
    def explain_creator_match(
        self,
        creator_id: int,
        job_id: int
    ) -> MatchExplanationResponse:
        """
        1. Fetch creator portfolio items, verified tools, and brief requirements.
        2. Prompt Groq to explain the match narrative with explicit citations to portfolio IDs.
        3. Return grounded narrative alongside the deterministic mathematical score breakdown.
        """
        pass
