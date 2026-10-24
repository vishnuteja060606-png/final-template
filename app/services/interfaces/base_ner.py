from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.advanced import NERExtractResponse, EntityItem

class BaseNERService(ABC):
    """
    Abstract Interface for Named Entity Recognition (NER) & Canonical Normalization.
    Assigned to: Member 3
    Technology: Hybrid Catalog/Regex matcher + Groq Structured JSON fallback
    """

    @abstractmethod
    def extract_entities(self, text: str, source_type: str = "creator_claim") -> NERExtractResponse:
        """
        Extract entities across categories:
        - AI tools and models (Midjourney, Runway Gen-3, Kling, Flux.1, ComfyUI, etc.)
        - Skills and specializations (Prompt Engineering, Upscaling, Inpainting, Storyboarding)
        - Creative styles (Cinematic, Anime, Hyper-realistic, 3D)
        - Formats and aspect ratios (16:9, 9:16, 1:1, MP4, PNG)
        - Licensing (Commercial Buyout, Exclusivity, Attribution)
        - Deadlines & budgets
        """
        pass

    @abstractmethod
    def normalize_to_canonical(self, category: str, raw_token: str) -> str:
        """
        Normalize aliases into database canonical values.
        Example: 'MJ v6' -> 'Midjourney v6', 'vertical reel' -> '9:16'.
        """
        pass

    @abstractmethod
    def persist_extracted_entities(
        self,
        entity_type: str,
        entity_id: int,
        extracted: NERExtractResponse
    ) -> None:
        """
        Persist normalized entities into the `extracted_entities` sidecar table with provenance tags.
        """
        pass
